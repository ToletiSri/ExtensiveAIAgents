Run("mspaint.exe")
Sleep(2000)  ; Wait for Paint to open

; Maximize the Paint window to fill the screen
WinActivate("ahk_class MSPaintApp")  ; Activate Paint window
WinMaximize("ahk_class MSPaintApp")  ; Maximize the Paint window

; Open the Resize dialog for the canvas (Ctrl + E)
;Send("^e")  ; Open the Resize dialog for canvas
;Sleep(500)  ; Wait for the window to open

; Resize the canvas to 1920x1080 (Full HD)
;Send("1920{Tab}1080{Enter}")  ; Set canvas to 1920x1080 pixels

; Ensure focus is on the Home tab (Alt + H)
Send("!h")  ; Alt+H to focus the Home tab
Sleep(500)  ; Wait for the Home tab to open


