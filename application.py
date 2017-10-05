from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Playlist, SongItem

app = Flask(__name__)

engine = create_engine('sqlite:///playlist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/playlists/<int:playlist_id>/JSON')
def playlistListJSON(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    items = session.query(SongItem).filter_by(playlist_id=playlist_id).all()
    return jsonify(SongItems=[i.serialize for i in items])

# ADD JSON ENDPOINT HERE
@app.route('/playlists/<int:playlist_id>/<int:song_id>/JSON')
def menuItemJSON(playlist_id, song_id):
    songItem = session.query(SongItem).filter_by(id=song_id).one()
    return jsonify(SongItem=songItem.serialize)

@app.route('/')
@app.route('/playlists/<int:playlist_id>/')
def playlistsPage(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    items = session.query(SongItem).filter_by(playlist_id=playlist.id)
    return render_template('list.html', playlist=playlist, items=items)
    

# Create new playlist songs
@app.route('/playlists/<int:playlist_id>/new/', methods=['GET', 'POST'])
def newSongItem(playlist_id):
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


@app.route('/playlists/<int:playlist_id>/<int:song_id>/edit/', methods=['GET', 'POST'])
def editSongItem(playlist_id, song_id):
    editedItem = session.query(SongItem).filter_by(id=song_id).one()
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



@app.route('/playlists/<int:playlist_id>/<int:song_id>/delete/', methods=['GET', 'POST'])
def deleteSongItem(playlist_id, song_id):
    itemToDelete = session.query(SongItem).filter_by(id=song_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        # TODO: Specific name of the song.
        flash("Song has been deleted!")
        return redirect(url_for('playlistsPage', playlist_id=playlist_id))
    else:
        return render_template('deletesongitem.html', item=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
