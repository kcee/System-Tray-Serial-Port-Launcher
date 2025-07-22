COM Port Launcher - 智慧型 COM Port 啟動器
這是一個基於 Python 的 Windows 系統匣工具，旨在為經常需要使用序列埠（COM Port）的開發者、工程師或愛好者提供便利。它會常駐在系統右下角，動態偵測並列出所有可用的 COM Port 設備，並允許使用者快速透過 PuTTY 連線。

✨ 功能特色
系統匣常駐：以一個簡潔的圖示常駐在 Windows 系統匣，不打擾您的工作區。

動態 COM Port 偵測：

即時列表：右鍵點擊圖示，即可看到目前系統上所有已連接的 COM Port 設備列表。

詳細資訊提示：滑鼠懸停在圖示上時，會以氣泡提示（Tooltip）的方式條列出所有 COM Port 的裝置名稱及其描述。

一鍵 PuTTY 啟動：在右鍵選單中直接點擊任一 COM Port，即可自動使用預設的鮑率（Baud Rate）開啟 PuTTY 並進行連線。

靈活的鮑率設定：

透過 .ini 設定檔儲存預設鮑率，方便管理。若設定檔不存在，則自動建立並預設為 115200。

提供圖形化設定介面，可從常用鮑率中選擇，或手動輸入自訂值。

開機自動啟動管理：

在選單中提供可打勾的選項，讓使用者一鍵設定或取消開機時自動執行。

操作後會以系統通知提供即時狀態回饋，使用者體驗更佳。

智慧型操作鎖定：當使用者開啟設定視窗或修改開機啟動選項時，選單中的其他主要操作會暫時禁用（變灰），防止因快速重複點擊而產生衝突或錯誤。

📋 環境需求
作業系統: Windows 10 或更高版本

Python 版本: Python 3.9+

必要的 Python 套件:

pyserial

pystray

Pillow

winshell

外部依賴:

PuTTY: 程式預期 putty.exe 存在於系統的環境變數 PATH 中。如果沒有，使用者需要手動修改腳本中的 PUTTY_PATH 變數。

🚀 安裝與執行
1. 從原始碼執行
如果您想直接從 Python 原始碼執行此工具，請依照以下步驟操作：

a. 複製儲存庫

Bash

git clone [您的 GitHub 儲存庫網址]
cd [儲存庫名稱]
b. 安裝相依套件

建議先建立一個 requirements.txt 檔案，內容如下：

pyserial
pystray
Pillow
winshell
然後透過 pip 進行安裝：

Bash

pip install -r requirements.txt
c. 執行主程式

假設您的主程式檔名為 com_port_launcher.py：

Bash

python com_port_launcher.py
程式啟動後，您就可以在系統右下角看到藍色的 "COM" 圖示了。

2. 使用已打包的 .exe 執行檔
對於不熟悉 Python 的使用者，可以將此工具打包成單一的 .exe 檔來發佈。

a. 安裝打包工具

Bash

pip install pyinstaller
b. 執行打包指令

請先準備一個 .ico 格式的圖示檔（可透過程式第一次執行時自動生成的 .png 轉換而來）。然後在專案根目錄下執行：

Bash

pyinstaller --onefile --windowed --icon=your_icon.ico com_port_launcher.py
c. 取得成品

打包完成後，最終的執行檔會位於 dist 資料夾內。使用者只需執行這個 .exe 檔即可。

💡 使用方法
執行程式：直接執行 .exe 檔或 python 腳本。

查看 COM Ports：將滑鼠移到系統匣的圖示上，即可看到目前所有設備的列表。

開啟 PuTTY：在圖示上按右鍵，從選單頂部選擇您想連線的 COM Port。

設定鮑率：在右鍵選單中點擊「設定鮑率...」，在跳出的視窗中設定並儲存。

設定開機啟動：在右鍵選單中點擊「開機時自動啟動」。此選項會自動打勾或取消打勾，並跳出系統通知告知您目前的狀態。

結束程式：在右鍵選單中點擊「離開」。

這個專案是為了解決特定需求而生，若您有任何建議或發現問題，歡迎提出 Issue！
