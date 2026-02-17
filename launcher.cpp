#include <windows.h>
#include <shellapi.h>
#include <string>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    // 获取当前 exe 所在的路径
    wchar_t exePath[MAX_PATH];
    GetModuleFileNameW(NULL, exePath, MAX_PATH);

    // 去掉文件名，得到 exe 所在目录
    std::wstring path(exePath);
    size_t pos = path.find_last_of(L"\\");
    if (pos != std::wstring::npos)
    {
        path = path.substr(0, pos + 1); // 保留末尾的反斜杠
    }

    // 构造 AppDatas 下 Main.pyw 的完整路径
    std::wstring targetPath = path + L"AppDatas\\Main.pyw";

    // 构造工作目录（AppDatas 文件夹）
    std::wstring workDir = path + L"AppDatas";

    // 使用 ShellExecute 打开 .pyw 文件
    HINSTANCE result = ShellExecuteW(
        NULL,
        L"open",
        targetPath.c_str(),
        NULL,
        workDir.c_str(),
        SW_SHOWNORMAL
    );

    // 如果返回错误码小于等于32，表示启动失败
    if ((int)result <= 32)
    {
        MessageBoxW(NULL, L"无法启动 MineCodes，请确保已安装 Python 并正确关联 .pyw 文件。", L"启动失败", MB_ICONERROR);
        return 1;
    }

    return 0;
}