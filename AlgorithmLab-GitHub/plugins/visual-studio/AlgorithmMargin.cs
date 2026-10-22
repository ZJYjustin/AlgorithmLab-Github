using System;
using System.ComponentModel.Composition;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;

namespace AlgorithmLab {
    [Export(typeof(IWpfTextViewMarginProvider))]
    [Name("AlgorithmLabMargin")]
    [MarginContainer(PredefinedMarginNames.Top)]
    [ContentType("code")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    public sealed class Provider : IWpfTextViewMarginProvider {
        [Import] internal ITextDocumentFactoryService Documents = null;
        public IWpfTextViewMargin CreateMargin(IWpfTextViewHost host, IWpfTextViewMargin container) {
            ITextDocument document;
            if (!Documents.TryGetTextDocument(host.TextView.TextBuffer, out document)) return null;
            string extension = Path.GetExtension(document.FilePath).ToLowerInvariant();
            if (extension != ".c" && extension != ".cpp" && extension != ".cc" && extension != ".cxx" && extension != ".py") return null;
            return new Margin(document);
        }
    }
    public sealed class Margin : IWpfTextViewMargin {
        readonly StackPanel panel;
        readonly CheckBox enabled;
        readonly ITextDocument document;
        bool disposed;
        static string Runtime { get {return Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), "runtime");} }
        public Margin(ITextDocument doc) {
            document = doc;
            panel = new StackPanel {Orientation=Orientation.Horizontal, Height=34, Background=new SolidColorBrush(Color.FromRgb(30,43,57))};
            enabled = new CheckBox {Content="Algorithm Lab",IsChecked=true,VerticalAlignment=VerticalAlignment.Center,Foreground=Brushes.White,Margin=new Thickness(10,0,8,0)};
            panel.Children.Add(enabled);
            Button run = new Button {Content="可视化当前文件",Margin=new Thickness(2,4,6,4),Padding=new Thickness(8,0,8,0)};
            run.Click += delegate {Run(false);};panel.Children.Add(run);
            Button lines = new Button {Content="Python 逐行",Margin=new Thickness(2,4,6,4),Padding=new Thickness(8,0,8,0)};
            lines.Click += delegate {Run(true);};panel.Children.Add(lines);
            Button settings = new Button {Content="设置 Python",Margin=new Thickness(2,4,6,4),Padding=new Thickness(8,0,8,0)};
            settings.Click += delegate {
                var dialog = new Microsoft.Win32.OpenFileDialog {Title="选择 Python 解释器", Filter="Python interpreter|python.exe;pythonw.exe|Executable|*.exe"};
                if(dialog.ShowDialog()==true) File.WriteAllText(Path.Combine(Runtime,"python.path"),dialog.FileName);
            };panel.Children.Add(settings);
            Action sync = delegate {run.IsEnabled=lines.IsEnabled=enabled.IsChecked==true;};
            enabled.Checked += delegate {sync();};enabled.Unchecked += delegate {sync();};
        }
        void Run(bool lines) {
            if(enabled.IsChecked!=true)return;
            if(lines && !document.FilePath.EndsWith(".py",StringComparison.OrdinalIgnoreCase)) {
                MessageBox.Show("逐行模式支持 Python；C/C++ 请使用记录接口后选择“可视化当前文件”。","Algorithm Lab");return;
            }
            try {
                document.Save();
                string python=File.ReadAllText(Path.Combine(Runtime,"python.path")).Trim();
                string windowless=Path.Combine(Path.GetDirectoryName(python),"pythonw.exe");
                if(File.Exists(windowless)) python=windowless;
                var info=new ProcessStartInfo {FileName=python,Arguments=Quote(Path.Combine(Runtime,"lab.py"))+" "+Quote(document.FilePath)+(lines?" --mode lines":""),WorkingDirectory=Runtime,UseShellExecute=false,CreateNoWindow=true};
                Process.Start(info);
            } catch(Exception ex) {MessageBox.Show(ex.Message,"Algorithm Lab 启动失败");}
        }
        static string Quote(string value) {return "\""+value.Replace("\"","\\\"")+"\"";}
        public FrameworkElement VisualElement {get {return panel;}}
        public double MarginSize {get {return panel.ActualHeight;}}
        public bool Enabled {get {return !disposed;}}
        public ITextViewMargin GetTextViewMargin(string name) {return string.Equals(name,"AlgorithmLabMargin",StringComparison.OrdinalIgnoreCase)?this:null;}
        public void Dispose() {disposed=true;}
    }
}
