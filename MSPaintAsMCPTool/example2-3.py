# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import time
import subprocess

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        ahk_path = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe"
        draw_rectangle_ahk = "paint_draw_rectangle.ahk"
        
        # Generate the AHK script dynamically for writing text (v2 syntax)
        ahk_script_content = f"""

        ; Set starting coordinates for the rectangle (top-left corner)
        startX := {x1}
        startY := {y1}
        endX := {x2}
        endY := {y2}

        ; Move the mouse to the starting position of the rectangle
        MouseMove(startX, startY)

        ; Press down the mouse button to begin drawing the rectangle (Click Down)
        Click startX, startY, 1, "D"  ; "D" means mouse button is held down (left button)

        ; Move the mouse diagonally to the bottom-right corner (forming a rectangle)
        MouseMove(startX, endY)    ; Move both horizontally and vertically to draw the rectangle

        ; Release the mouse button to finish drawing the rectangle (Click Up)
        Click startX, endY, 1, "U"  ; "U" means mouse button is released (left button)

        Sleep(500)

        ; Press down the mouse button to begin drawing the rectangle (Click Down)
        Click startX, endY, 1, "D"  ; "D" means mouse button is held down (left button)

        ; Move the mouse diagonally to the bottom-right corner (forming a rectangle)
        MouseMove(endX, endY)    ; Move both horizontally and vertically to draw the rectangle

        ; Release the mouse button to finish drawing the rectangle (Click Up)
        Click endX, endY, 1, "U"  ; "U" means mouse button is released (left button)

        Sleep(500)

        ; Press down the mouse button to begin drawing the rectangle (Click Down)
        Click endX, endY, 1, "D"  ; "D" means mouse button is held down (left button)

        ; Move the mouse diagonally to the bottom-right corner (forming a rectangle)
        MouseMove(endX, startY)    ; Move both horizontally and vertically to draw the rectangle

        ; Release the mouse button to finish drawing the rectangle (Click Up)
        Click endX, startY, 1, "U"  ; "U" means mouse button is released (left button)

        Sleep(500)

        ; Press down the mouse button to begin drawing the rectangle (Click Down)
        Click endX, startY, 1, "D"  ; "D" means mouse button is held down (left button)

        ; Move the mouse diagonally to the bottom-right corner (forming a rectangle)
        MouseMove(startX, startY)    ; Move both horizontally and vertically to draw the rectangle

        ; Release the mouse button to finish drawing the rectangle (Click Up)
        Click startX, startY, 1, "U"  ; "U" means mouse button is released (left button)

        """

        # Save the dynamically generated AHK script
        with open(draw_rectangle_ahk, "w", encoding="utf-8") as file:
            file.write(ahk_script_content)

        
        # Type the text passed from client
        subprocess.run([ahk_path, draw_rectangle_ahk])
        time.sleep(0.5)


        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text: rectangle added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }
    
@mcp.tool()
async def write_text(text: str, x1: int, y1: int, x2: int, y2: int) -> dict:
    """Write text in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        ahk_path = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe"
        # Paths to AHK scripts (Update with actual paths)
        write_text_ahk = "paint_write_text.ahk"

        # Dynamic text to be written in Paint
        custom_text = text

        # Generate the AHK script dynamically for writing text (v2 syntax)
        ahk_script_content = f"""

        ; Select Text Tool using ALT → T → X
        Send "{{Alt Down}}"  ; Press ALT key
        Sleep 100
        Send "{{Alt Up}}"    ; Release ALT key
        Sleep 100
        Send "t"           ; Press T
        Sleep 100
        Send "x"           ; Press X
        Sleep 200          ; Wait for Paint to activate text mode


        ; Click and drag to create a text box
        startX := {x1}
        startY := {y1}
        endX := {x2}
        endY := {y2}

        MouseMove(startX, startY)
        Click "Down"
        MouseMove(endX, endY, 50)  ; Dragging motion
        Click "Up"

        Sleep 500  ; Wait for text box activation

        A_Clipboard := "{custom_text}"  ; Copy text to clipboard
        Sleep(500)
        Send("^v")  ; Paste the text (Ctrl + V)
        """

        # Save the dynamically generated AHK script
        with open(write_text_ahk, "w", encoding="utf-8") as file:
            file.write(ahk_script_content)

        # Write Dynamic Text
        print(f"Writing Text: {custom_text}")
        subprocess.run([ahk_path, write_text_ahk])

    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    try:
        # Path to AutoHotkey executable
        ahk_path = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe" 
        open_paint_ahk = "D:\\SRT_Courses\\TSAI\\EAG\\Session3\\paint_open.ahk"

        subprocess.run([ahk_path, open_paint_ahk])
        time.sleep(0.5) #Wait for paint to open
        paint_app = True
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully on secondary monitor and maximized"
                )
            ]
        }
    except Exception as e:
        paint_app = False
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
