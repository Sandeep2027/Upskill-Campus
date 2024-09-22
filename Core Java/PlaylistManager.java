import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class PlaylistManager {
    private List<File> playlist = new ArrayList<>();
    private String playlistName;

    public PlaylistManager(String playlistName) {
        this.playlistName = playlistName;
    }

    public void addSong(File file) {
        playlist.add(file);
    }

    public void removeSong(File file) {
        playlist.remove(file);
    }

    public List<File> getPlaylist() {
        return playlist;
    }

    public String getPlaylistName() {
        return playlistName;
    }
}
