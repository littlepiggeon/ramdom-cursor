from cmd import Cmd
from os import getenv, remove
import winreg


KEYS = (
    "Arrow",
    "Help",
    "AppStarting",
    "Wait",
    "Crosshair",
    "IBeam",
    "Hand",
    "No",
    "SizeNS",
    "SizeWE",
    "SizeNWSE",
    "SizeNESW",
    "SizeAll",
    "UpArrow",
    "Link",
)


class App(Cmd):
    intro = """这是让你的计算机可以在每次唤醒时自动更换鼠标指针的程序。
    键入a或activate来激活，键入d或deactivate来停用，quit退出。
    """
    prompt = ">>> "

    def do_activate(self, _):
        """激活自动更换鼠标指针功能"""
        with open(
            f"{getenv('APPDATA')}\\Microsoft\\Windows\\Start Menu\\Programs\\change_cursor.ps1",
            "w",
        ) as f:
            f.write("$commands={\n")

            reg = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Cursors\Schemes",
                0,
                winreg.KEY_READ,
            )
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(reg, i)
                    if value:
                        f.write(
                            f'reg add "HKCU\\Control Panel\\Cursors" /ve /t REG_SZ /d "{name}" /f\n'
                        )
                        values = value.split(",",14)
                        if len(values) < 15:
                            values.extend([""] * (15 - len(values)))
                        for key, name in zip(KEYS, values):
                            f.write(
                                f"reg add \"HKCU\\Control Panel\\Cursors\" /v {key} /t REG_EXPAND_SZ /d \"{name.strip(', ')}\" /f\n"
                            )
                            # print(key,name) # debug
                    i += 1
                    f.write("},{\n")
                except OSError:
                    f.write("}\n")
                    break

            f.write(
                """$randomCommand=Get-Random -InputObject $commands
& $randomCommand

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class CursorHelper {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);
}
"@

[CursorHelper]::SystemParametersInfo(0x0057, 0, [IntPtr]::Zero, 0x01)
"""
            )

        with open(f"{getenv('APPDATA')}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\random_cursor.bat",'w') as f2:
            f2.write("powershell ../change_cursor.ps1")
        print("已激活。")

    def do_a(self, _):
        """激活自动更换鼠标指针功能"""
        self.do_activate(_)

    def do_deactivate(self, _):
        """停用自动更换鼠标指针功能"""
        try:
            remove(
                f"{getenv('APPDATA')}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\random_cursor.bat"
            )
            print("已停用。")
        except FileNotFoundError:
            print("未找到自动更换鼠标指针的启动项，可能已经停用。")

    def do_d(self, _):
        """停用自动更换鼠标指针功能"""
        self.do_deactivate(_)

    def do_quit(self, _):
        """退出程序"""
        return True


if __name__ == "__main__":
    App().cmdloop()
