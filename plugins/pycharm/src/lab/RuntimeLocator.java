package lab;

import com.intellij.ide.plugins.PluginManagerCore;
import com.intellij.openapi.extensions.PluginId;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** Resolve bundled files through the IDE plugin descriptor, not CodeSource.
 * JetBrains' plugin class loader can have a CodeSource with a null location.
 */
public final class RuntimeLocator {
    private RuntimeLocator() {}

    public static Path locate() throws IOException {
        var descriptor = PluginManagerCore.getPlugin(PluginId.getId("local.algorithm.lab"));
        if (descriptor == null || descriptor.getPluginPath() == null) {
            throw new IOException("无法取得 Algorithm Lab 的安装目录，请重新安装插件并重启 PyCharm。");
        }
        Path home = descriptor.getPluginPath().resolve("runtime").toAbsolutePath().normalize();
        if (!Files.isRegularFile(home.resolve("lab.py")) || !Files.isRegularFile(home.resolve("python.path"))) {
            throw new IOException("Algorithm Lab 安装文件不完整，缺少 runtime/lab.py 或 python.path：" + home);
        }
        return home;
    }
}
