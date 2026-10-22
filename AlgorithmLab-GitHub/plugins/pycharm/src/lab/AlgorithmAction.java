package lab;

import com.intellij.ide.util.PropertiesComponent;
import com.intellij.openapi.actionSystem.*;
import com.intellij.openapi.application.ApplicationManager;
import com.intellij.openapi.fileEditor.FileDocumentManager;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.vfs.VirtualFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class AlgorithmAction extends AnAction {
    static Path runtime() throws Exception {
        return RuntimeLocator.locate();
    }
    @Override public ActionUpdateThread getActionUpdateThread() { return ActionUpdateThread.BGT; }
    @Override public void update(AnActionEvent event) {
        VirtualFile file = event.getData(CommonDataKeys.VIRTUAL_FILE);
        boolean supported = file != null && file.getExtension() != null &&
            Set.of("py", "c", "cpp", "cc", "cxx").contains(file.getExtension().toLowerCase());
        if (lines() && file != null && !"py".equalsIgnoreCase(file.getExtension())) supported = false;
        event.getPresentation().setEnabled(supported && PropertiesComponent.getInstance().getBoolean("AlgorithmLab.enabled", true));
    }
    protected boolean lines() { return false; }
    @Override public void actionPerformed(AnActionEvent event) {
        VirtualFile file = event.getData(CommonDataKeys.VIRTUAL_FILE);
        if (file == null) return;
        var document = FileDocumentManager.getInstance().getDocument(file);
        if (document != null) FileDocumentManager.getInstance().saveDocument(document);
        String path = file.getPath();
        ApplicationManager.getApplication().executeOnPooledThread(() -> {
            try {
                Path home = runtime();
                String python = PropertiesComponent.getInstance().getValue("AlgorithmLab.python",
                    Files.readString(home.resolve("python.path"), StandardCharsets.UTF_8).trim());
                Path interpreter = Path.of(python);
                Path windowless = interpreter.resolveSibling("pythonw.exe");
                if (Files.isRegularFile(windowless)) interpreter = windowless;
                ArrayList<String> command = new ArrayList<>(List.of(interpreter.toString(), home.resolve("lab.py").toString(), path));
                if (lines()) { command.add("--mode"); command.add("lines"); }
                ProcessBuilder launcher = new ProcessBuilder(command).directory(home.toFile())
                    .redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(home.resolve("launcher.log").toFile()));
                // The runner and its worker must use the same selected interpreter.
                launcher.environment().put("ALGORITHM_LAB_PYTHON", python);
                launcher.start();
            } catch (Exception ex) {
                ApplicationManager.getApplication().invokeLater(() -> Messages.showErrorDialog(event.getProject(),
                    ex.getMessage(), "Algorithm Lab"));
            }
        });
    }
    public static final class Lines extends AlgorithmAction {
        @Override protected boolean lines() { return true; }
    }
    public static final class Enable extends ToggleAction {
        @Override public ActionUpdateThread getActionUpdateThread() { return ActionUpdateThread.BGT; }
        @Override public boolean isSelected(AnActionEvent e) { return PropertiesComponent.getInstance().getBoolean("AlgorithmLab.enabled", true); }
        @Override public void setSelected(AnActionEvent e, boolean value) { PropertiesComponent.getInstance().setValue("AlgorithmLab.enabled", value, true); }
    }
    public static final class Configure extends AnAction {
        @Override public void actionPerformed(AnActionEvent e) {
            try {
                String fallback = Files.readString(runtime().resolve("python.path"), StandardCharsets.UTF_8).trim();
                String selected = Messages.showInputDialog(e.getProject(), "Python 解释器的完整路径（python.exe）：",
                    "Algorithm Lab · Python", null, PropertiesComponent.getInstance().getValue("AlgorithmLab.python", fallback), null);
                if (selected != null && !selected.isBlank()) {
                    if (!Files.isRegularFile(Path.of(selected))) throw new Exception("找不到该解释器文件。");
                    PropertiesComponent.getInstance().setValue("AlgorithmLab.python", selected);
                }
            } catch (Exception ex) { Messages.showErrorDialog(e.getProject(), ex.getMessage(), "Algorithm Lab"); }
        }
    }
}
