#!/usr/bin/env python3
"""
Enhanced Tkinter GUI for the Financial Document Redactor with realistic data and detailed reporting.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.redactor import FinancialDocumentRedactor


class EnhancedRedactorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 PDF Document Redactor - Enhanced Edition")

        # Set minimum window size and make it resizable
        self.root.minsize(1000, 700)
        self.root.geometry("1200x900")  # Larger default size for Windows

        # Configure window to be properly resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Initialize redactor with realistic mode by default
        self.redactor = FinancialDocumentRedactor()
        self.redactor.update_config({"replacement_mode": "realistic"})
        
        self.selected_files = []
        self.output_folder = ""
        self.processing = False
        self.redaction_reports = {}
        
        self.setup_ui()
        
        # Log startup message
        self.log_message("🚀 PDF Document Redactor Enhanced Edition")
        self.log_message("✨ Default mode: Realistic fake data replacement")
        self.log_message("📋 Select PDF files to get started!")
    
    def setup_ui(self):
        # Create top content frame and bottom button frame for better layout
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Main frame with padding in content area
        main_frame = ttk.Frame(content_frame, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Title with icon
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="📄 PDF Document Redactor", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, padx=(0, 10))
        
        subtitle_label = ttk.Label(title_frame, text="Enhanced Edition with Realistic Data", 
                                 font=("Arial", 12), foreground="gray")
        subtitle_label.grid(row=1, column=0)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings", padding="15")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(settings_frame, text="Replacement Mode:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        self.mode_var = tk.StringVar(value="realistic")
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.mode_var, 
                                 values=["realistic", "generic", "custom"], 
                                 state="readonly", width=35, font=("Arial", 10))
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # Mode descriptions
        descriptions_frame = ttk.Frame(settings_frame)
        descriptions_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.mode_desc = ttk.Label(descriptions_frame, 
                                  text="🎭 Realistic: Replaces with believable fake data (John Smith, 555-123-4567)",
                                  font=("Arial", 9), foreground="blue")
        self.mode_desc.grid(row=0, column=0, sticky=tk.W)
        
        # Configuration display frame
        config_frame = ttk.Frame(settings_frame)
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(config_frame, text="🔍 Detection Categories:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        self.config_display = ttk.Label(config_frame, text="Loading configuration...",
                                       font=("Arial", 9), foreground="darkgreen",
                                       wraplength=600)
        self.config_display.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Custom strings replacement frame
        custom_frame = ttk.LabelFrame(settings_frame, text="🎯 Custom String Replacement", padding="10")
        custom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))

        # Instructions
        ttk.Label(custom_frame, text="Add specific strings to replace (one per line):",
                 font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Input area frame
        input_area_frame = ttk.Frame(custom_frame)
        input_area_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Original strings input
        ttk.Label(input_area_frame, text="Original strings:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.original_strings_text = tk.Text(input_area_frame, height=4, width=35, font=("Courier", 9))
        self.original_strings_text.grid(row=1, column=0, padx=(0, 10), pady=(5, 0))

        # Replacement text input
        ttk.Label(input_area_frame, text="Replace with:", font=("Arial", 9)).grid(row=0, column=1, sticky=tk.W)

        replacement_frame = ttk.Frame(input_area_frame)
        replacement_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))

        self.replacement_text = tk.StringVar(value="[REDACTED]")
        replacement_entry = ttk.Entry(replacement_frame, textvariable=self.replacement_text,
                                    width=20, font=("Arial", 9))
        replacement_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Buttons frame
        buttons_frame = ttk.Frame(input_area_frame)
        buttons_frame.grid(row=1, column=2, padx=(10, 0), pady=(5, 0))

        ttk.Button(buttons_frame, text="✅ Add",
                  command=self.add_custom_strings, width=8).grid(row=0, column=0, pady=(0, 5))
        ttk.Button(buttons_frame, text="🗑️ Clear",
                  command=self.clear_custom_strings, width=8).grid(row=1, column=0)

        # Current custom strings display
        ttk.Label(custom_frame, text="Current custom strings:",
                 font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        self.custom_strings_display = scrolledtext.ScrolledText(custom_frame, height=4, state="disabled",
                                                              font=("Courier", 9), wrap=tk.WORD)
        self.custom_strings_display.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))

        # Configure grid weights for custom frame
        custom_frame.grid_columnconfigure(0, weight=1)
        input_area_frame.grid_columnconfigure(1, weight=1)
        replacement_frame.grid_columnconfigure(0, weight=1)
        
        # File selection frame
        files_frame = ttk.LabelFrame(main_frame, text="📁 File Selection", padding="15")
        files_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(file_btn_frame, text="📂 Select PDF Files", 
                  command=self.select_files).grid(row=0, column=0, padx=(0, 10))
        
        self.files_label = ttk.Label(file_btn_frame, text="No files selected", font=("Arial", 10))
        self.files_label.grid(row=0, column=1, sticky=tk.W)
        
        # Files preview area
        self.files_preview = scrolledtext.ScrolledText(files_frame, height=3, state="disabled", 
                                                      font=("Courier", 9))
        self.files_preview.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Output folder frame
        output_frame = ttk.LabelFrame(main_frame, text="📤 Output Location", padding="15")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(output_btn_frame, text="📁 Select Output Folder", 
                  command=self.select_output_folder).grid(row=0, column=0, padx=(0, 10))
        
        self.output_label = ttk.Label(output_btn_frame, text="No folder selected", font=("Arial", 10))
        self.output_label.grid(row=0, column=1, sticky=tk.W)
        
        # Move buttons to dedicated bottom frame for Windows compatibility
        # Buttons are now always visible (enabled based on file selection)
        self.preview_btn = ttk.Button(button_frame, text="👁️ Preview Detection",
                                     command=self.preview_detection, state="normal")
        self.preview_btn.pack(side="left", padx=(0, 10))

        self.process_btn = ttk.Button(button_frame, text="🔒 Process Documents",
                                     command=self.process_files, state="normal")
        self.process_btn.pack(side="left", padx=(0, 10))

        self.progress = ttk.Progressbar(button_frame, length=200, mode='indeterminate')
        self.progress.pack(side="left", padx=(10, 0))
        
        # Results area with tabs - now at row 4 since buttons moved to bottom
        results_frame = ttk.LabelFrame(main_frame, text="📊 Processing Results", padding="15")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Detection Preview tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="👁️ Detection Preview")
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, state="disabled",
                                                     font=("Courier", 9))
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Processing log tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📝 Processing Log")
        
        self.results_text = scrolledtext.ScrolledText(log_frame, height=10, state="disabled",
                                                     font=("Courier", 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Detailed redaction report tab
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="🔍 Redaction Details")
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=10, state="disabled",
                                                     font=("Courier", 9))
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📈 Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=10, state="disabled",
                                                     font=("Arial", 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for proper resizing
        main_frame.grid_rowconfigure(4, weight=1)  # Results frame gets expansion
        main_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        # Configure notebook tabs
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_rowconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize configuration display
        self.update_config_display()

        # Initialize custom strings display
        self.update_custom_strings_display()
    
    def on_mode_change(self, event=None):
        """Handle replacement mode change."""
        mode = self.mode_var.get()
        
        # Update descriptions
        descriptions = {
            "realistic": "🎭 Realistic: Replaces with believable fake data (John Smith, 555-123-4567)",
            "generic": "🏷️ Generic: Replaces with placeholders (XXX-XX-XXXX, [REDACTED])",
            "custom": "🔧 Custom: Uses your custom replacement values from config"
        }
        
        self.mode_desc.config(text=descriptions.get(mode, ""))
        
        try:
            self.redactor.update_config({"replacement_mode": mode})
            self.update_config_display()
            self.log_message(f"✅ Mode changed to: {mode.title()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update mode: {e}")
    
    def select_files(self):
        """Select PDF files to process."""
        files = filedialog.askopenfilenames(
            title="Select PDF Files to Process",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            multiple=True
        )
        
        if files:
            self.selected_files = list(files)
            count = len(self.selected_files)
            self.files_label.config(text=f"Selected {count} file(s)")
            
            # Update files preview
            self.files_preview.config(state="normal")
            self.files_preview.delete(1.0, tk.END)
            
            preview_text = f"📁 Selected {count} PDF files:\\n\\n"
            for i, file_path in enumerate(self.selected_files, 1):
                filename = os.path.basename(file_path)
                file_size = self.get_file_size(file_path)
                preview_text += f"{i:2d}. {filename} ({file_size})\\n"
                
            self.files_preview.insert(tk.END, preview_text)
            self.files_preview.config(state="disabled")
            
            self.log_message(f"📂 Selected {count} PDF files for processing")
            self.check_ready()
    
    def get_file_size(self, file_path):
        """Get human readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            else:
                return f"{size_bytes/(1024**2):.1f} MB"
        except:
            return "Unknown size"
    
    def select_output_folder(self):
        """Select output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder for Redacted Files")
        
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Output: {folder}")
            self.log_message(f"📁 Output folder: {folder}")
            self.check_ready()
    
    def check_ready(self):
        """Check if ready to process and update buttons."""
        # Always keep buttons visible and enabled for better user experience
        if self.selected_files and not self.processing:
            count = len(self.selected_files)
            self.preview_btn.config(state="normal", text=f"👁️ Preview {count} File(s)")

            if self.output_folder:
                self.process_btn.config(state="normal", text=f"🔒 Process {count} File(s)")
            else:
                self.process_btn.config(state="normal", text="🔒 Process Documents")
        else:
            # Keep buttons visible but show helpful text
            self.preview_btn.config(state="normal", text="👁️ Preview Detection")
            self.process_btn.config(state="normal", text="🔒 Process Documents")
    
    def log_message(self, message):
        """Add message to processing log."""
        self.results_text.config(state="normal")
        self.results_text.insert(tk.END, message + "\\n")
        self.results_text.see(tk.END)
        self.results_text.config(state="disabled")
        self.root.update_idletasks()
    
    def update_config_display(self):
        """Update the configuration display showing what will be detected."""
        try:
            config = self.redactor.config
            enabled_categories = config.get('enabled_categories', {})
            
            # Get enabled categories
            enabled = [name.replace('_', ' ').title() for name, enabled in enabled_categories.items() if enabled]
            
            if not enabled:
                config_text = "❌ No categories enabled for detection"
            else:
                # Create display text with emojis
                category_emojis = {
                    'Ssn': '🆔',
                    'Phone': '📞', 
                    'Account Number': '🏦',
                    'Routing Number': '🏧',
                    'Credit Card': '💳',
                    'Tax Id': '📋',
                    'Currency': '💰',
                    'Dates': '📅',
                    'Email': '📧',
                    'Address': '🏠',
                    'Employer': '🏢',
                    'Names': '👤'
                }
                
                categorized = []
                for cat in enabled:
                    emoji = category_emojis.get(cat, '🔍')
                    categorized.append(f"{emoji} {cat}")
                
                config_text = f"✅ Enabled: {', '.join(categorized)}"
            
            # Add replacement mode info
            mode = config.get('replacement_mode', 'generic')
            mode_info = {
                'realistic': 'with realistic fake data',
                'generic': 'with generic placeholders', 
                'custom': 'with custom replacements'
            }
            
            config_text += f" | 🔄 Replacing {mode_info.get(mode, mode)}"
            
            self.config_display.config(text=config_text)
            
        except Exception as e:
            self.config_display.config(text=f"⚠️ Error loading configuration: {e}")

    def add_custom_strings(self):
        """Add custom strings for replacement."""
        try:
            # Get input text
            input_text = self.original_strings_text.get("1.0", tk.END).strip()
            replacement = self.replacement_text.get().strip()

            if not input_text:
                messagebox.showwarning("Warning", "Please enter at least one string to replace.")
                return

            if not replacement:
                replacement = "[REDACTED]"

            # Split into individual strings (by lines)
            strings = [s.strip() for s in input_text.split('\n') if s.strip()]

            if not strings:
                messagebox.showwarning("Warning", "Please enter valid strings to replace.")
                return

            # Add to redactor
            success = self.redactor.add_custom_strings(strings, replacement, save=True)

            if success:
                # Clear input
                self.original_strings_text.delete("1.0", tk.END)

                # Update display
                self.update_custom_strings_display()

                # Log message
                self.log_message(f"✅ Added {len(strings)} custom string(s) for replacement with '{replacement}'")
                messagebox.showinfo("Success", f"Added {len(strings)} custom string(s) successfully!")
            else:
                messagebox.showerror("Error", "Failed to add custom strings.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add custom strings: {str(e)}")

    def clear_custom_strings(self):
        """Clear all custom strings."""
        try:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all custom strings?"):
                success = self.redactor.clear_custom_strings(save=True)

                if success:
                    # Update display
                    self.update_custom_strings_display()

                    # Log message
                    self.log_message("🗑️ Cleared all custom strings")
                    messagebox.showinfo("Success", "Cleared all custom strings successfully!")
                else:
                    messagebox.showerror("Error", "Failed to clear custom strings.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear custom strings: {str(e)}")

    def update_custom_strings_display(self):
        """Update the display of current custom strings."""
        try:
            # Get current custom strings
            custom_strings = self.redactor.get_custom_strings()

            # Enable text widget for update
            self.custom_strings_display.config(state="normal")
            self.custom_strings_display.delete("1.0", tk.END)

            if not custom_strings:
                self.custom_strings_display.insert("1.0", "No custom strings configured.")
            else:
                # Group by replacement text
                replacement_groups = {}
                for item in custom_strings:
                    replacement = item["replacement"]
                    if replacement not in replacement_groups:
                        replacement_groups[replacement] = []
                    replacement_groups[replacement].append(item["text"])

                # Display grouped strings
                lines = []
                for replacement, strings in replacement_groups.items():
                    lines.append(f"Replace with '{replacement}':")
                    for string in strings:
                        lines.append(f"  • {string}")
                    lines.append("")  # Empty line between groups

                display_text = "\n".join(lines).strip()
                self.custom_strings_display.insert("1.0", display_text)

            # Disable text widget again
            self.custom_strings_display.config(state="disabled")

        except Exception as e:
            # Enable for error message
            self.custom_strings_display.config(state="normal")
            self.custom_strings_display.delete("1.0", tk.END)
            self.custom_strings_display.insert("1.0", f"Error loading custom strings: {str(e)}")
            self.custom_strings_display.config(state="disabled")

    def process_files(self):
        """Start processing files in background thread."""
        if self.processing:
            return

        # Check if files are selected
        if not self.selected_files:
            messagebox.showwarning("No Files Selected",
                                 "Please select PDF files to process first.\n\n"
                                 "Click '📂 Select PDF Files' to choose files.")
            return

        # Check if output folder is selected
        if not self.output_folder:
            messagebox.showwarning("No Output Folder",
                                 "Please select an output folder first.\n\n"
                                 "Click '📁 Select Output Folder' to choose where to save redacted files.")
            return

        thread = threading.Thread(target=self._process_files_thread)
        thread.daemon = True
        thread.start()
    
    def redact_with_main_redactor(self, input_path: str, output_path: str) -> dict:
        """
        Use the main redactor to process PDF with same logic as CLI.
        Returns dict compatible with enhanced processor interface.
        """
        try:
            # Extract filename and folders for main redactor interface
            input_filename = os.path.basename(input_path)
            output_filename = os.path.basename(output_path)
            input_folder = os.path.dirname(input_path)
            output_folder = os.path.dirname(output_path)

            # Use main redactor (same as CLI)
            success = self.redactor.redact_pdf(
                input_pdf=input_filename,
                output_pdf=output_filename,
                input_folder=input_folder,
                output_folder=output_folder
            )

            if success:
                # Create a basic report (enhanced processor interface compatibility)
                report = {
                    'document_type': 'unknown',  # Could be enhanced later
                    'total_redactions': 0,  # Could be enhanced later
                    'redactions_by_category': {},
                    'detailed_redactions': []
                }

                return {
                    'success': True,
                    'redaction_report': report
                }
            else:
                return {
                    'success': False,
                    'error': 'Redaction failed'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _process_files_thread(self):
        """Process files in background thread with detailed reporting."""
        try:
            self.processing = True
            self.root.after(0, self._start_processing_ui)
            
            processed_files = []
            failed_files = []
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    filename = os.path.basename(file_path)
                    name_without_ext = os.path.splitext(filename)[0]
                    output_filename = f"{name_without_ext}_redacted.pdf"
                    output_path = os.path.join(self.output_folder, output_filename)
                    
                    # Log progress
                    self.root.after(0, self.log_message, 
                                  f"\\n🔄 Processing {i+1}/{len(self.selected_files)}: {filename}")
                    
                    # Use main redactor to ensure same logic as CLI
                    result = self.redact_with_main_redactor(file_path, output_path)
                    
                    if result['success']:
                        report = result['redaction_report']
                        processed_files.append({
                            "original": filename,
                            "output_path": output_path,
                            "report": report
                        })
                        
                        # Log success with details
                        self.root.after(0, self.log_message, f"✅ Success: {output_filename}")
                        self.root.after(0, self.log_message, 
                                      f"   📊 Document type: {report['document_type']}")
                        self.root.after(0, self.log_message, 
                                      f"   🔒 Total redactions: {report['total_redactions']}")
                        
                        if report['redactions_by_category']:
                            category_summary = ", ".join([f"{cat}: {count}" for cat, count in report['redactions_by_category'].items()])
                            self.root.after(0, self.log_message, f"   📋 Categories: {category_summary}")
                    
                    else:
                        failed_files.append(filename)
                        error_msg = result.get('error', 'Unknown error')
                        self.root.after(0, self.log_message, f"❌ Failed: {filename}")
                        self.root.after(0, self.log_message, f"   Error: {error_msg}")
                        
                except Exception as e:
                    failed_files.append(filename)
                    self.root.after(0, self.log_message, f"❌ Error processing {filename}: {str(e)}")
            
            # Finish processing
            self.root.after(0, self._finish_processing_ui, processed_files, failed_files)
            
        except Exception as e:
            self.root.after(0, self.log_message, f"❌ Critical error: {str(e)}")
            self.root.after(0, self._finish_processing_ui, [], [])
    
    def _start_processing_ui(self):
        """Update UI when processing starts."""
        self.process_btn.config(state="disabled", text="⏳ Processing...")
        self.progress.start()
        self.log_message("\\n" + "="*70)
        self.log_message("🚀 Starting document processing...")
        self.log_message(f"🎛️  Mode: {self.mode_var.get().title()}")
        self.log_message("="*70)
    
    def _finish_processing_ui(self, processed_files, failed_files):
        """Update UI when processing finishes."""
        self.processing = False
        self.progress.stop()
        self.check_ready()
        
        # Log completion
        self.log_message("\\n" + "="*70)
        self.log_message("🎉 Processing Complete!")
        self.log_message("="*70)
        self.log_message(f"✅ Successfully processed: {len(processed_files)}")
        self.log_message(f"❌ Failed: {len(failed_files)}")
        self.log_message(f"📊 Total files: {len(self.selected_files)}")
        
        if processed_files:
            total_redactions = sum(file_info['report']['total_redactions'] for file_info in processed_files)
            self.log_message(f"🔒 Total items redacted: {total_redactions}")
            self.log_message(f"📁 Files saved to: {self.output_folder}")
        
        # Generate detailed reports
        if processed_files:
            self._generate_detailed_report(processed_files)
            self._generate_summary_report(processed_files)
        
        # Show completion dialog
        if processed_files:
            total_redactions = sum(file_info['report']['total_redactions'] for file_info in processed_files)
            messagebox.showinfo("Processing Complete", 
                               f"🎉 Successfully processed {len(processed_files)} of {len(self.selected_files)} files!\\n\\n"
                               f"🔒 Total items redacted: {total_redactions}\\n\\n"
                               f"📁 Files saved to:\\n{self.output_folder}\\n\\n"
                               f"📊 Check the tabs above for detailed reports.")
        else:
            messagebox.showerror("Error", "❌ No files were processed successfully!")
    
    def _generate_detailed_report(self, processed_files):
        """Generate detailed redaction report."""
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        
        header = "="*80 + "\\n"
        header += "🔍 DETAILED REDACTION REPORT\\n"
        header += "="*80 + "\\n\\n"
        self.details_text.insert(tk.END, header)
        
        for file_info in processed_files:
            report = file_info['report']
            filename = file_info['original']
            
            # File header
            file_header = f"📄 FILE: {filename}\\n"
            file_header += f"📋 Document Type: {report['document_type'].title()}\\n"
            file_header += f"🔒 Total Redactions: {report['total_redactions']}\\n"
            file_header += "-" * 60 + "\\n\\n"
            self.details_text.insert(tk.END, file_header)
            
            # Category summary
            if report['redactions_by_category']:
                self.details_text.insert(tk.END, "📊 REDACTIONS BY CATEGORY:\\n")
                for category, count in report['redactions_by_category'].items():
                    category_name = category.replace('_', ' ').title()
                    self.details_text.insert(tk.END, f"  • {category_name}: {count} items\\n")
                self.details_text.insert(tk.END, "\\n")
            
            # Detailed redactions
            if report['detailed_redactions']:
                self.details_text.insert(tk.END, "🔍 DETAILED REPLACEMENTS:\\n\\n")
                
                for i, redaction in enumerate(report['detailed_redactions'][:30]):  # Limit to 30 per file
                    category = redaction['category'].replace('_', ' ').title()
                    original = redaction['original']
                    replacement = redaction['replacement']
                    page = redaction['page']
                    
                    entry = f"{i+1:2d}. [{category}] Page {page}\\n"
                    entry += f"    📝 Original:     '{original}'\\n"
                    entry += f"    🔄 Replaced with: '{replacement}'\\n\\n"
                    
                    self.details_text.insert(tk.END, entry)
                
                if len(report['detailed_redactions']) > 30:
                    remaining = len(report['detailed_redactions']) - 30
                    self.details_text.insert(tk.END, f"    ... and {remaining} more redactions\\n\\n")
            
            self.details_text.insert(tk.END, "="*60 + "\\n\\n")
        
        self.details_text.config(state="disabled")
    
    def _generate_summary_report(self, processed_files):
        """Generate summary report."""
        self.summary_text.config(state="normal")
        self.summary_text.delete(1.0, tk.END)
        
        # Summary header
        summary = "📈 PROCESSING SUMMARY REPORT\\n"
        summary += "="*50 + "\\n\\n"
        
        total_files = len(processed_files)
        total_redactions = sum(file_info['report']['total_redactions'] for file_info in processed_files)
        
        summary += f"📊 Files processed: {total_files}\\n"
        summary += f"🔒 Total redactions: {total_redactions}\\n"
        summary += f"🎛️ Replacement mode: {self.mode_var.get().title()}\\n\\n"
        
        # Category totals across all files
        category_totals = {}
        doc_types = {}
        
        for file_info in processed_files:
            report = file_info['report']
            
            # Count document types
            doc_type = report['document_type']
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Sum up categories
            for category, count in report['redactions_by_category'].items():
                category_totals[category] = category_totals.get(category, 0) + count
        
        # Document types
        summary += "📄 DOCUMENT TYPES:\\n"
        for doc_type, count in doc_types.items():
            summary += f"  • {doc_type.title()}: {count} file(s)\\n"
        summary += "\\n"
        
        # Category totals
        if category_totals:
            summary += "🏷️ REDACTION CATEGORIES (Total across all files):\\n"
            for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                category_name = category.replace('_', ' ').title()
                percentage = (total / total_redactions * 100) if total_redactions > 0 else 0
                summary += f"  • {category_name}: {total} items ({percentage:.1f}%)\\n"
            summary += "\\n"
        
        # File-by-file summary
        summary += "📋 FILE-BY-FILE SUMMARY:\\n"
        summary += "-" * 50 + "\\n"
        
        for i, file_info in enumerate(processed_files, 1):
            report = file_info['report']
            filename = file_info['original']
            
            summary += f"{i:2d}. {filename}\\n"
            summary += f"    Type: {report['document_type'].title()}\\n"
            summary += f"    Redactions: {report['total_redactions']}\\n"
            
            if report['redactions_by_category']:
                categories = [f"{cat}({count})" for cat, count in report['redactions_by_category'].items()]
                summary += f"    Categories: {', '.join(categories)}\\n"
            
            summary += "\\n"
        
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state="disabled")

    def preview_detection(self):
        """Preview what content will be detected and replaced."""
        # Check if files are selected
        if not self.selected_files:
            messagebox.showwarning("No Files Selected",
                                 "Please select PDF files to preview first.\n\n"
                                 "Click '📂 Select PDF Files' to choose files for preview.")
            return

        # Start preview in background thread
        thread = threading.Thread(target=self._preview_detection_thread)
        thread.daemon = True
        thread.start()
    
    def _preview_detection_thread(self):
        """Preview detection in background thread."""
        try:
            # Switch to preview tab
            self.root.after(0, lambda: self.notebook.select(0))  # Select first tab (preview)
            
            self.root.after(0, self._start_preview_ui)
            
            # Clear preview area
            self.root.after(0, self._clear_preview)
            
            all_detections = {}
            
            for i, file_path in enumerate(self.selected_files):
                filename = os.path.basename(file_path)
                
                self.root.after(0, self._update_preview, 
                              f"🔍 Analyzing file {i+1}/{len(self.selected_files)}: {filename}")
                
                try:
                    # Extract text from PDF
                    import fitz
                    doc = fitz.open(file_path)
                    full_text = ""
                    for page in doc:
                        full_text += page.get_text()
                    doc.close()
                    
                    if not full_text.strip():
                        self.root.after(0, self._update_preview, f"   ⚠️  No text found in {filename}")
                        continue
                    
                    # Use same pattern logic as main redactor (includes custom strings)
                    enabled_patterns = self.redactor.get_enabled_patterns()

                    # Group patterns by category for display
                    active_patterns = {}
                    for pattern, replacement in enabled_patterns:
                        # Try to determine category from replacement text
                        category = "unknown"
                        if "FULL NAME" in replacement:
                            category = "names"
                        elif "XXX-XX-XXXX" in replacement:
                            category = "ssn"
                        elif "XXX-XXX-XXXX" in replacement:
                            category = "phone"
                        elif "XXXXXXXXXX" in replacement:
                            category = "account_number"
                        elif "$X,XXX.XX" in replacement:
                            category = "currency"
                        elif "user@domain.com" in replacement:
                            category = "email"
                        elif "STREET ADDRESS" in replacement or "CITY, STATE" in replacement:
                            category = "address"
                        elif "[CUSTOM_REDACTED]" in replacement or "[REDACTED]" in replacement:
                            category = "custom_strings"

                        if category not in active_patterns:
                            active_patterns[category] = []
                        active_patterns[category].append((pattern, replacement))
                    
                    # Find all matches
                    file_detections = {}
                    import re
                    
                    for category, pattern_list in active_patterns.items():
                        matches = []
                        for pattern, replacement in pattern_list:
                            try:
                                if pattern.startswith('\\\\b') and pattern.endswith('\\\\b'):
                                    # NLP exact match
                                    match_text = pattern.replace('\\\\b', '').replace('\\\\', '')
                                    if match_text in full_text:
                                        matches.append((match_text, replacement))
                                else:
                                    # Regex pattern
                                    found_matches = re.finditer(pattern, full_text, re.IGNORECASE)
                                    for match in found_matches:
                                        matches.append((match.group(), replacement))
                            except Exception:
                                continue
                        
                        if matches:
                            # Generate realistic replacements for preview
                            realistic_matches = []
                            for original, generic_replacement in matches:
                                if self.redactor.config.get("replacement_mode") == "realistic":
                                    realistic_replacement = self.redactor.generate_realistic_replacement(category, original)
                                else:
                                    realistic_replacement = generic_replacement
                                realistic_matches.append((original, realistic_replacement))
                            
                            file_detections[category] = realistic_matches
                    
                    all_detections[filename] = file_detections
                    
                except Exception as e:
                    self.root.after(0, self._update_preview, f"   ❌ Error analyzing {filename}: {str(e)}")
                    continue
            
            # Display results
            self.root.after(0, self._display_preview_results, all_detections)
            
        except Exception as e:
            self.root.after(0, self._update_preview, f"❌ Preview error: {str(e)}")
        finally:
            self.root.after(0, self._finish_preview_ui)
    
    def _start_preview_ui(self):
        """Start preview UI updates."""
        self.preview_btn.config(state="disabled", text="🔍 Analyzing...")
        self.progress.start()
    
    def _finish_preview_ui(self):
        """Finish preview UI updates."""
        self.preview_btn.config(state="normal")
        self.progress.stop()
        self.check_ready()
    
    def _clear_preview(self):
        """Clear the preview text area."""
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state="disabled")
    
    def _update_preview(self, message):
        """Update preview with a message."""
        self.preview_text.config(state="normal")
        self.preview_text.insert(tk.END, message + "\\n")
        self.preview_text.see(tk.END)
        self.preview_text.config(state="disabled")
        self.root.update_idletasks()
    
    def _display_preview_results(self, all_detections):
        """Display the preview results."""
        self.preview_text.config(state="normal")
        
        header = "="*80 + "\\n"
        header += "👁️ SENSITIVE CONTENT DETECTION PREVIEW\\n"
        header += "="*80 + "\\n\\n"
        self.preview_text.insert(tk.END, header)
        
        total_items = 0
        
        for filename, file_detections in all_detections.items():
            if not file_detections:
                continue
                
            file_header = f"📄 FILE: {filename}\\n"
            file_header += "-" * 60 + "\\n\\n"
            self.preview_text.insert(tk.END, file_header)
            
            file_total = 0
            for category, matches in file_detections.items():
                if not matches:
                    continue
                    
                category_name = category.replace('_', ' ').title()
                self.preview_text.insert(tk.END, f"🏷️ {category_name.upper()} ({len(matches)} items):\\n")
                
                # Show up to 10 examples per category
                for i, (original, replacement) in enumerate(matches[:10]):
                    self.preview_text.insert(tk.END, f"   '{original}' → '{replacement}'\\n")
                    file_total += 1
                    total_items += 1
                
                if len(matches) > 10:
                    remaining = len(matches) - 10
                    self.preview_text.insert(tk.END, f"   ... and {remaining} more items\\n")
                    file_total += remaining
                    total_items += remaining
                
                self.preview_text.insert(tk.END, "\\n")
            
            if file_total > 0:
                self.preview_text.insert(tk.END, f"📊 Total items in this file: {file_total}\\n\\n")
        
        if total_items > 0:
            summary = f"🎯 SUMMARY: Found {total_items} sensitive items across {len(all_detections)} files\\n"
            summary += f"🔄 Replacement mode: {self.redactor.config.get('replacement_mode', 'generic').title()}\\n"
            summary += f"💡 Click 'Process Documents' to apply these replacements to new files.\\n"
        else:
            summary = "✅ No sensitive content detected in the selected files.\\n"
        
        self.preview_text.insert(tk.END, "="*80 + "\\n")
        self.preview_text.insert(tk.END, summary)
        self.preview_text.insert(tk.END, "="*80 + "\\n")
        
        self.preview_text.config(state="disabled")


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Set application icon and properties
    root.title("📄 PDF Document Redactor - Enhanced Edition")
    
    try:
        app = EnhancedRedactorGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()