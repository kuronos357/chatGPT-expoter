import json
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def get_conversations(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Invalid JSON", f"The file '{file_path}' is not a valid JSON file.")
        return None

def export_selected(conversations, selected_indices, output_dir):
    if not selected_indices:
        messagebox.showinfo("No Selection", "Please select at least one conversation to export.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in selected_indices:
        conv = conversations[i]
        title = conv.get("title", "untitled").replace("/", "_").replace("\\", "_")
        mapping = conv.get("mapping", {})

        def extract_messages(mapping):
            ordered = []
            visited = set()
            def dfs(node_id):
                if node_id in visited or node_id not in mapping:
                    return
                visited.add(node_id)
                msg = mapping[node_id].get("message")
                if msg:
                    role = msg["author"].get("role", "unknown")
                    parts = msg["content"].get("parts", [])
                    content_parts = []
                    if parts:
                        for part in parts:
                            if isinstance(part, dict):
                                content_parts.append(part.get("text", ""))
                            elif isinstance(part, str):
                                content_parts.append(part)
                    content = "\n".join(content_parts) if content_parts else ""
                    ordered.append((role, content))
                for child_id in mapping[node_id].get("children", []):
                    dfs(child_id)
            root_ids = [k for k, v in mapping.items() if v.get("parent") is None]
            for root in root_ids:
                dfs(root)
            return ordered

        messages = extract_messages(mapping)

        filename = f"{output_dir}/{title[:50]}.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["role", "content"])
            writer.writerows(messages)

    messagebox.showinfo("Export Complete", f"Selected conversations have been exported to '{output_dir}'.")

def main():
    root = tk.Tk()
    root.title("ChatGPT Exporter")

    # --- Input Path ---
    input_frame = tk.Frame(root)
    input_frame.pack(pady=5, padx=10, fill=tk.X)

    input_label = tk.Label(input_frame, text="Input JSON File:")
    input_label.pack(side=tk.LEFT)

    input_path_var = tk.StringVar(value="Project/chatGPTexporter/conversations.json")
    input_entry = tk.Entry(input_frame, textvariable=input_path_var, width=50)
    input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def browse_input_file():
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            input_path_var.set(file_path)
            load_conversations()

    browse_input_button = tk.Button(input_frame, text="Browse...", command=browse_input_file)
    browse_input_button.pack(side=tk.LEFT)

    # --- Output Path ---
    output_frame = tk.Frame(root)
    output_frame.pack(pady=5, padx=10, fill=tk.X)

    output_label = tk.Label(output_frame, text="Output Directory:")
    output_label.pack(side=tk.LEFT)

    output_path_var = tk.StringVar(value="Project/chatGPTexporter/出力")
    output_entry = tk.Entry(output_frame, textvariable=output_path_var, width=50)
    output_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def browse_output_dir():
        dir_path = filedialog.askdirectory()
        if dir_path:
            output_path_var.set(dir_path)

    browse_output_button = tk.Button(output_frame, text="Browse...", command=browse_output_dir)
    browse_output_button.pack(side=tk.LEFT)

    # --- Conversation List ---
    listbox_frame = tk.Frame(root)
    listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, width=80, height=20)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    conversations = []

    def load_conversations():
        nonlocal conversations
        file_path = input_path_var.get()
        data = get_conversations(file_path)
        if data:
            conversations = data
            listbox.delete(0, tk.END)
            for conv in conversations:
                listbox.insert(tk.END, conv.get("title", "untitled"))

    # --- Export Button ---
    export_button = tk.Button(root, text="Export Selected", command=lambda: export_selected(conversations, listbox.curselection(), output_path_var.get()))
    export_button.pack(pady=5)

    # Initial load
    load_conversations()

    root.mainloop()

if __name__ == "__main__":
    main()