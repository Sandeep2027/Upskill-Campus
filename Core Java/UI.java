import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.util.List;

public class UI {
    private MusicPlayer musicPlayer = new MusicPlayer();
    private PlaylistManager playlistManager = new PlaylistManager("Default Playlist");
    private LibraryManager libraryManager = new LibraryManager();

    private JFrame frame;
    private JButton playButton, pauseButton, stopButton, loadButton, nextButton, prevButton, shuffleButton, repeatButton;
    private JSlider volumeSlider;
    private JList<File> musicList;
    private JTextArea metadataDisplay;
    private boolean isShuffling = false;
    private boolean isRepeating = false;

    public void createAndShowGUI() {
        frame = new JFrame("Music Player");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(600, 400);
        frame.setLayout(new BorderLayout());

        musicList = new JList<>(new DefaultListModel<>());
        frame.add(new JScrollPane(musicList), BorderLayout.CENTER);

        metadataDisplay = new JTextArea(3, 40);
        metadataDisplay.setEditable(false);
        frame.add(new JScrollPane(metadataDisplay), BorderLayout.NORTH);

        JPanel controlPanel = new JPanel();
        frame.add(controlPanel, BorderLayout.SOUTH);

        playButton = new JButton("Play");
        pauseButton = new JButton("Pause");
        stopButton = new JButton("Stop");
        nextButton = new JButton("Next");
        prevButton = new JButton("Previous");
        loadButton = new JButton("Load");
        shuffleButton = new JButton("Shuffle");
        repeatButton = new JButton("Repeat");

        volumeSlider = new JSlider(0, 100, 50);
        volumeSlider.setPreferredSize(new Dimension(200, 30));

        controlPanel.add(playButton);
        controlPanel.add(pauseButton);
        controlPanel.add(stopButton);
        controlPanel.add(nextButton);
        controlPanel.add(prevButton);
        controlPanel.add(loadButton);
        controlPanel.add(shuffleButton);
        controlPanel.add(repeatButton);
        controlPanel.add(volumeSlider);

        playButton.addActionListener(e -> playMusic());
        pauseButton.addActionListener(e -> musicPlayer.pause());
        stopButton.addActionListener(e -> musicPlayer.stop());
        nextButton.addActionListener(e -> {
            musicPlayer.nextTrack();
            updateMetadata();
        });
        prevButton.addActionListener(e -> {
            musicPlayer.prevTrack();
            updateMetadata();
        });
        loadButton.addActionListener(e -> loadMusic());
        shuffleButton.addActionListener(e -> toggleShuffle());
        repeatButton.addActionListener(e -> toggleRepeat());

        volumeSlider.addChangeListener(e -> {
            float volume = volumeSlider.getValue() / 100f;
            musicPlayer.setVolume(volume);
        });

        frame.setVisible(true);
    }

    private void loadMusic() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setMultiSelectionEnabled(true);
        int returnValue = fileChooser.showOpenDialog(null);
        if (returnValue == JFileChooser.APPROVE_OPTION) {
            File[] files = fileChooser.getSelectedFiles();
            for (File file : files) {
                libraryManager.addMusicFile(file);
                ((DefaultListModel<File>) musicList.getModel()).addElement(file);
            }
        }
    }

    private void playMusic() {
        File selectedFile = musicList.getSelectedValue();
        if (selectedFile != null) {
            try {
                musicPlayer.loadFile(selectedFile);
                musicPlayer.play();
                updateMetadata();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void updateMetadata() {
        File selectedFile = musicList.getSelectedValue();
        if (selectedFile != null) {
            metadataDisplay.setText("Now Playing: " + selectedFile.getName());
        }
    }

    private void toggleShuffle() {
        isShuffling = !isShuffling;
        musicPlayer.setShuffle(isShuffling);
        shuffleButton.setText(isShuffling ? "Shuffle (On)" : "Shuffle");
    }

    private void toggleRepeat() {
        isRepeating = !isRepeating;

        musicPlayer.setRepeat(isRepeating);
        repeatButton.setText(isRepeating ? "Repeat (On)" : "Repeat");
    }
}

