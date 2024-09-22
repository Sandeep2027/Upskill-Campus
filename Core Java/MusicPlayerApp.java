import javax.swing.SwingUtilities;

public class MusicPlayerApp {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            UI ui = new UI();
            ui.createAndShowGUI();
        });
    }
}
