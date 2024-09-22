import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class LibraryManager {
    private List<File> musicFiles = new ArrayList<>();
    private List<File> taggedFiles = new ArrayList<>();

    public void addMusicFile(File file) {
        if (file.exists() && (file.getName().endsWith(".mp3") || file.getName().endsWith(".wav") || file.getName().endsWith(".flac"))) {
            musicFiles.add(file);
        }
    }

    public List<File> searchByArtist(String artist) {
        return musicFiles.stream()
                .filter(file -> file.getName().contains(artist))
                .collect(Collectors.toList());
    }

    public List<File> searchByAlbum(String album) {
        return musicFiles.stream()
                .filter(file -> file.getName().contains(album))
                .collect(Collectors.toList());
    }

    public List<File> getMusicFiles() {
        return musicFiles;
    }

    public void tagFile(File file) {
        taggedFiles.add(file);
    }

    public List<File> getTaggedFiles() {
        return taggedFiles;
    }
}
