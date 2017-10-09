from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Playlist, SongItem, User
import random, string
import httplib2
import json
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "HEar Me hear You Application"

engine = create_engine('sqlite:///playlist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# ADD JSON ENDPOINT HERE
@app.route('/playlists/<int:playlist_id>/JSON')
def playlistListJSON(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    items = session.query(SongItem).filter_by(playlist_id=playlist_id).all()
    return jsonify(SongItems=[i.serialize for i in items])

@app.route('/playlists/<int:playlist_id>/<int:song_id>/JSON')
def menuItemJSON(playlist_id, song_id):
    songItem = session.query(SongItem).filter_by(id=song_id).one()
    return jsonify(SongItem=songItem.serialize)
# END JSON ENDPOINTS

# HOME page
@app.route('/')
@app.route('/playlists/')
def homePage():
    playlists = session.query(Playlist).all()
    return render_template('homePage.html', playlists=playlists)

# PLAYLIST pages
@app.route('/playlists/<int:playlist_id>/')
def playlistsPage(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    items = session.query(SongItem).filter_by(playlist_id=playlist.id)
    return render_template('list.html', playlist=playlist, items=items)

# Create a new playlist
@app.route('/playlists/new/', methods=['GET', 'POST'])
def newPlaylistItem():
    # Only need to check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newPlaylist = Playlist(user_id=login_session['user_id'], 
                               name=request.form['name'], 
                               description=request.form['description'])
        session.add(newPlaylist)
        session.commit()
        flash("New playlist has been added!")
        return redirect(url_for('playlistsPage', playlist_id=newPlaylist.id))
    else:
        return render_template('newplaylistitem.html')

# Edit a playlist
@app.route('/playlists/<int:playlist_id>/edit/', methods=['GET', 'POST'])
def editPlaylistItem(playlist_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this playlist.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            playlist.name = request.form['name']
        if request.form['description']:
            playlist.description = request.form['description']
        session.add(playlist)
        session.commit()
        # TODO: Specific name of the playlist.
        flash("The playlist has been edited!")
        return redirect(url_for('playlistsPage', playlist_id=playlist_id))
    else:
        return render_template(
            'editplaylistitem.html', playlist=playlist)

# Delete a playlist
@app.route('/playlists/<int:playlist_id>/delete/', methods=['GET', 'POST'])
def deletePlaylistItem(playlist_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    itemToDelete = session.query(SongItem).filter_by(playlist_id=playlist.id).all()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this whole playlist.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        for i in itemToDelete:
            session.delete(i)
        session.delete(playlist)
        session.commit()
        # TODO: Specific name of the song.
        flash("The playlist and all its songs have been deleted!")
        return redirect(url_for('homePage'))
    else:
        return render_template('deleteplaylistitem.html', playlist=playlist, item=itemToDelete)


# SONG pages
    

# Create new playlist songs
@app.route('/playlists/<int:playlist_id>/new/', methods=['GET', 'POST'])
def newSongItem(playlist_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add songs to this playlist. Please create your own playlist in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        # TODO: Need to fix this
        newItem = SongItem(user_id=1,
            name=request.form['name'], link=request.form['link'],
            genre=request.form['genre'], playlist_id=playlist_id)
        session.add(newItem)
        session.commit()
        flash("New song has been added!")
        return redirect(url_for('playlistsPage', playlist_id=playlist_id))
    else:
        return render_template('newsongitem.html', playlist_id=playlist_id)

# Edit playlists songs
@app.route('/playlists/<int:playlist_id>/<int:song_id>/edit/', methods=['GET', 'POST'])
def editSongItem(playlist_id, song_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(SongItem).filter_by(id=song_id).one()
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit song items to this playlist. Please create your own playlist in order to edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['genre']:
            editedItem.genre = request.form['genre']
        if request.form['link']:
            editedItem.link = request.form['link']
        session.add(editedItem)
        session.commit()
        # TODO: Specific name of the song.
        flash("The song has been edited!")
        return redirect(url_for('playlistsPage', playlist_id=playlist_id))
    else:
        return render_template(
            'editsongitem.html', playlist_id=playlist_id, song_id=song_id, item=editedItem)

# Delete playlists songs
@app.route('/playlists/<int:playlist_id>/<int:song_id>/delete/', methods=['GET', 'POST'])
def deleteSongItem(playlist_id, song_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    itemToDelete = session.query(SongItem).filter_by(id=song_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete song items to this playlist. Please create your own playlist in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        # TODO: Specific name of the song.
        flash("Song has been deleted!")
        return redirect(url_for('playlistsPage', playlist_id=playlist_id))
    else:
        return render_template('deletesongitem.html', item=itemToDelete)


# Logins
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r' ).read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

     # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print 'valid state token'
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    print code
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    
    try:
        # Upgrade the authorization code into a credentials object
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    
    # Submite request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID does not match"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    
    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    flash("You are now logged in as %s" %login_session['username'])
    print "Done!"
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    if result['status'] == 200:
        del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # The given token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect - revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    print 'In gdisconnect access token is %s', access_token
    print 'Username is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %login_session['access_token']
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # The given token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('homePage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('homePage'))

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
