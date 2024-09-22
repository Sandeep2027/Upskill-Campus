import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;
import java.util.Random;

public class MusicPlayer {
    private Clip clip;
    private AudioInputStream audioInputStream;
    private boolean isShuffling = false;
    private boolean isRepeating = false;
    private Random random = new Random();
    private File[] playlist;
    private int currentTrackIndex = 0;

    public void loadFile(File file) throws UnsupportedAudioFileException, IOException, LineUnavailableException {
        audioInputStream = AudioSystem.getAudioInputStream(file);
        clip = AudioSystem.getClip();
        clip.open(audioInputStream);
    }

    public void play() {
        if (clip != null) {
            clip.setFramePosition(0);
            clip.start();
            if (isRepeating) {
                clip.loop(Clip.LOOP_CONTINUOUSLY);
            }
        }
    }

    public void pause() {
        if (clip != null && clip.isRunning()) {
            clip.stop();
        }
    }

    public void stop() {
        if (clip != null) {
            clip.stop();
            clip.setFramePosition(0);
        }
    }

    public void setVolume(float volume) {
        if (clip != null) {
            FloatControl volumeControl = (FloatControl) clip.getControl(FloatControl.Type.VOLUME);
            volumeControl.setValue(volume);
        }
    }

    public void seek(int milliseconds) {
        if (clip != null) {
            clip.setMicrosecondPosition(milliseconds * 1000);
        }
    }

    public void setShuffle(boolean shuffle) {
        this.isShuffling = shuffle;
    }

    public void setRepeat(boolean repeat) {
        this.isRepeating = repeat;
    }

    public void nextTrack() {
        if (isShuffling) {
            currentTrackIndex = random.nextInt(playlist.length);
        } else {
            currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
        }
        loadTrack(playlist[currentTrackIndex]);
        play();
    }

    public void prevTrack() {
        if (isShuffling) {
            currentTrackIndex = random.nextInt(playlist.length);
        } else {
            currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
        }
        loadTrack(playlist[currentTrackIndex]);
        play();
    }

    public void loadTrack(File file) {
        try {
            loadFile(file);
            play();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
