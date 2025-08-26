import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import pandas as pd
import os
#the goal for this script is to compare two .csv files. It'll perform this action by merging two CSV's and compare the selected column's. It will output a file with only like-items remaining, it will add every cell from both docs as long as the selected columns have matching data
class OverlapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV User Overlap Finder")
        self.files = []
        self.dataframes = []

        self.instructions = ttk.Label(root, text="Drag and drop two CSV files below.\nSelect one column from each file to match on.\nClick 'Find Overlap' to merge users found in both lists.")
        self.instructions.pack(padx=10, pady=10)

        self.drop_zone = ttk.Label(root, text="Drop CSV files here", background="lightgray", anchor="center", width=50, padding=20)
        self.drop_zone.pack(padx=10, pady=(0,10))
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_drop)

        self.file_list = tk.Listbox(root, height=4, width=80)
        self.file_list.pack(padx=10, pady=(0,10))

        frm = ttk.Frame(root)
        frm.pack(padx=10, pady=(0,10), fill='x')

        self.col1_label = ttk.Label(frm, text="File 1 column:")
        self.col1_label.grid(row=0, column=0, sticky='w', padx=(0,4))
        self.col1_combo = ttk.Combobox(frm, state="readonly", width=30)
        self.col1_combo.grid(row=0, column=1, sticky='w', padx=(0,10))

        self.col2_label = ttk.Label(frm, text="File 2 column:")
        self.col2_label.grid(row=0, column=2, sticky='w', padx=(10,4))
        self.col2_combo = ttk.Combobox(frm, state="readonly", width=30)
        self.col2_combo.grid(row=0, column=3, sticky='w')

        self.process_button = ttk.Button(root, text="Find Overlap", command=self.find_overlap, state='disabled')
        self.process_button.pack(padx=10, pady=10)

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for path in paths:
            if path.lower().endswith(".csv") and path not in self.files and len(self.files) < 2:
                self.files.append(path)
                self.file_list.insert(tk.END, os.path.basename(path))
        if len(self.files) == 2:
            self.load_files()
        if len(self.files) > 2:
            messagebox.showwarning("Too many files", "Only two files can be processed at a time.")

    def load_files(self):
        try:
            self.dataframes = []
            columns1 = []
            columns2 = []
            for i, file in enumerate(self.files):
                df = pd.read_csv(file, dtype=str)
                self.dataframes.append(df)
                if i == 0:
                    columns1 = list(df.columns)
                else:
                    columns2 = list(df.columns)
            if not columns1 or not columns2:
                messagebox.showerror("Error", "Could not read columns from files.")
                return
            self.col1_combo['values'] = columns1
            self.col2_combo['values'] = columns2
            self.col1_combo.set(columns1[0])
            self.col2_combo.set(columns2[0])
            self.process_button['state'] = 'normal'
        except Exception as e:
            messagebox.showerror("Error loading files", str(e))
            self.files = []
            self.file_list.delete(0, tk.END)
            self.process_button['state'] = 'disabled'

    def find_overlap(self):
        try:
            col1 = self.col1_combo.get()
            col2 = self.col2_combo.get()
            if not col1 or not col2:
                messagebox.showerror("No Column Selected", "Please select columns to match on from both files.")
                return
            df1, df2 = self.dataframes

            # Standardize keys for matching: strip, uppercase
            df1['_key'] = df1[col1].astype(str).str.strip().str.upper()
            df2['_key'] = df2[col2].astype(str).str.strip().str.upper()

            # Merge on _key, keep only matches
            merged = pd.merge(df1, df2, on='_key', suffixes=('_file1', '_file2'))

            # Insert the matched value as the first column, with a clear label
            merged.insert(0, f'Matched ({col1} / {col2})', merged['_key'])
            merged.drop('_key', axis=1, inplace=True)

            # Prompt save location
            outname = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save merged users as..."
            )
            if not outname:
                return
            merged.to_csv(outname, index=False)
            messagebox.showinfo("Done", f"Found {len(merged)} matching users.\nOutput: {outname}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    import sys
    try:
        import pandas
        import tkinterdnd2
    except ImportError:
        print("You need to install 'pandas' and 'tkinterdnd2':\n\npip install pandas tkinterdnd2")
        sys.exit(1)
    root = TkinterDnD.Tk()
    app = OverlapApp(root)
    root.mainloop()