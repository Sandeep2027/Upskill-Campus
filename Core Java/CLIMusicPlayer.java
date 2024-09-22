import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class CLIMusicPlayer {
    private Process playerProcess;
    private List<String> playlist = new ArrayList<>();
    private int currentTrackIndex = 0;

    public void addTrack(String filePath) {
        playlist.add(filePath);
    }

    public void play() {
        if (currentTrackIndex >= 0 && currentTrackIndex < playlist.size()) {
            String filePath = playlist.get(currentTrackIndex);
            try {
                if (playerProcess != null && playerProcess.isAlive()) {
                    playerProcess.destroy();
                }
                playerProcess = new ProcessBuilder("mplayer", filePath).start();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void nextTrack() {
        currentTrackIndex = (currentTrackIndex + 1) % playlist.size();
        play();
    }

    public void prevTrack() {
        currentTrackIndex = (currentTrackIndex - 1 + playlist.size()) % playlist.size();
        play();
    }

    public void stop() {
        if (playerProcess != null && playerProcess.isAlive()) {
            playerProcess.destroy();
        }
    }

    public static void main(String[] args) {
        CLIMusicPlayer musicPlayer = new CLIMusicPlayer();
        musicPlayer.addTrack("/path/to/song1.mp3");
        musicPlayer.addTrack("/path/to/song2.mp3");

        musicPlayer.play();  // Start playing the first track

        // Add your CLI-based interactions here
    }
}

