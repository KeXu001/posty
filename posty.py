
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class FilepathEntry(tk.Frame):
  def __init__(self, parent, textvariable=None, *args, **kwargs):
    super(FilepathEntry, self).__init__(parent)

    self.text_var = textvariable

    self.entry = tk.Entry(self, textvariable=self.text_var)
    self.entry.pack(expand=True, fill=tk.X, side=tk.LEFT)

    self.button = tk.Button(self, text='Browse', padx=0, pady=0, command=self.on_button_press)
    self.button.pack(side=tk.RIGHT)

  def on_button_press(self):
    selected = filedialog.askopenfilename()

    if len(selected) > 0:
      if self.text_var is not None:
        self.text_var.set(selected)

class TextArea(tk.Text): # stackoverflow.com/questions/21507178
  def __init__(self, parent, textvariable=None, *args, **kwargs):
    super(TextArea, self).__init__(parent, *args, **kwargs)

    if textvariable is not None:
      if not isinstance(textvariable, tk.Variable):
        raise TypeError('tkinter.Variable expected')
      self._var = textvariable
      self._var_modified()
      self._text_trace = self.bind('<<Modified>>', self._text_modified)
      self._var_trace = self._var.trace('w', self._var_modified)

  def _text_modified(self, *args):
    if self._var is not None:
      self._var.trace_vdelete('w', self._var_trace)
      self._var.set(self.get(1.0, tk.END))
      self._var_trace = self._var.trace('w', self._var_modified)
      self.edit_modified(False)

  def _var_modified(self, *args):
    self.delete(1.0, tk.END)
    new_val = self._var.get()
    if new_val is not None:
      self.insert(tk.END, new_val)

class ScrollableTextArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    super(ScrollableTextArea, self).__init__(parent)

    self.text_area = TextArea(self, *args, **kwargs)
    self.text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    self.scrollbar = tk.Scrollbar(self, takefocus=False)
    self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.text_area.config(yscrollcommand=self.scrollbar.set)
    self.scrollbar.config(command=self.text_area.yview)

class ViewModel:
  def __init__(self):
    self.config_verify = tk.IntVar()
    self.config_verify.set(1)
    self.config_ca_cert = tk.StringVar()
    self.config_client_cert = tk.StringVar()
    self.config_client_key = tk.StringVar()

    self.request_method = tk.StringVar()
    self.request_method_options = ['GET', 'POST', 'PUT', 'DELETE']
    self.request_url = tk.StringVar()
    self.request_headers = tk.StringVar()
    self.request_body = tk.StringVar()

    self.response_status = tk.StringVar()
    self.response_headers = tk.StringVar()
    self.response_body=tk.StringVar()

  def go(self):
    method = self.request_method.get().upper()

    url = self.request_url.get()

    headers = dict()
    for line in self.request_headers.get().split('\n'):
      if len(line) == 0:
        continue

      parts = line.split(':')
      if len(parts) == 2:
        key = parts[0].strip()
        value = parts[1].strip()

        headers[key] = value
      else:
        raise ValueError('Bad syntax for headers')

    data = self.request_body.get()

    prep_args = dict()

    if self.config_verify.get():
      if self.config_ca_cert.get():
        prep_args['verify'] = self.config_ca_cert.get()
      else:
        prep_args['verify'] = True

      if not url.startswith('https://'):
        raise ValueError('URL must start with https:// if configured to Verify')
    else:
      prep_args['verify'] = False

    client_cert = self.config_client_cert.get()
    client_key = self.config_client_key.get()
    if client_cert and client_key:
      prep_args['cert'] = (client_cert, client_key)
    elif client_cert and not client_key:
      raise ValueError('Must provide Client Key if providing Client Cert')
    elif not client_cert and client_key:
      raise ValueError('Most provide Client Cert if providing Client Key')

    # clear response

    self.response_status.set('')
    self.response_headers.set('')
    self.response_body.set('')

    sess = requests.Session()
    req = requests.Request(method=method, url=url, headers=headers, data=data)
    prepped = sess.prepare_request(req)

    resp = sess.send(prepped, **prep_args)

    self.response_status.set(str(resp.status_code))
    self.response_headers.set('\n'.join(k + ': ' + v for k,v in resp.headers.items()))
    self.response_body.set(resp.text)
    
class Posty:

  class TabView:
    padding = {
      'padx': 5,
      'pady': 5
    }

    def __init__(self, parent, view_model):
      self.frame = tk.Frame(parent)
      self.frame.grid_columnconfigure(0, weight=0)
      self.frame.grid_columnconfigure(1, weight=1)
      self.frame.pack(expand=1, fill='both')

      self.row_count = 0

    def add_item(self, row_weight, title, item_generator, **grid_kwargs):
      self.frame.grid_rowconfigure(self.row_count, weight=row_weight)

      label = tk.Label(self.frame, text=title)
      label.grid(row=self.row_count, column=0, sticky='w', **self.padding)

      item = item_generator(self.frame)
      item.grid(row=self.row_count, column=1, **self.padding, **grid_kwargs)

      self.row_count += 1

  class ConfigTabView(TabView):
    def __init__(self, parent, view_model):
      super(Posty.ConfigTabView, self).__init__(parent, view_model)

      self.add_item(0, 'Verify',
        lambda parent: tk.Checkbutton(parent, variable=view_model.config_verify),
        sticky='w')

      self.add_item(0, 'CA Cert',
        lambda parent: FilepathEntry(parent, textvariable=view_model.config_ca_cert),
        sticky='ew')

      self.add_item(0, 'Client Cert',
        lambda parent: FilepathEntry(parent, textvariable=view_model.config_client_cert),
        sticky='ew')

      self.add_item(0, 'Client Key',
        lambda parent: FilepathEntry(parent, textvariable=view_model.config_client_key),
        sticky='ew')

  class RequestTabView(TabView):
    def __init__(self, parent, view_model):
      super(Posty.RequestTabView, self).__init__(parent, view_model)

      self.add_item(0, 'Method',
        lambda parent: ttk.Combobox(parent, textvariable=view_model.request_method, values=view_model.request_method_options),
        sticky='w')

      self.add_item(0, 'URL',
        lambda parent: tk.Entry(parent, textvariable=view_model.request_url),
        sticky='ew')

      self.add_item(0, 'Headers',
        lambda parent: ScrollableTextArea(parent, textvariable=view_model.request_headers, height=8, spacing1=8),
        sticky='nsew')

      self.add_item(0, 'Body',
        lambda parent: ScrollableTextArea(parent, textvariable=view_model.request_body, height=8, spacing1=8),
        sticky='nsew')

  class ResponseTabView(TabView):
    def __init__(self, parent, view_model):
      super(Posty.ResponseTabView, self).__init__(parent, view_model)

      self.add_item(0, 'Request',
        lambda parent: ttk.Button(parent, text='Send', command=view_model.go),
        sticky='w')

      self.add_item(0, 'Status',
        lambda parent: tk.Entry(parent, textvariable=view_model.response_status),
        sticky='ew')

      self.add_item(0, 'Headers',
        lambda parent: ScrollableTextArea(parent, textvariable=view_model.response_headers, height=8, spacing1=8),
        sticky='nsew')

      self.add_item(0, 'Body',
        lambda parent: ScrollableTextArea(parent, textvariable=view_model.response_body, height=8, spacing1=8),
        sticky='nsew')

  class MainView:
    def __init__(self, root, view_model):
      self.notebook = ttk.Notebook(root)
      self.notebook.pack(expand=True, fill='both')

      self.config_tab_view = Posty.ConfigTabView(self.notebook, view_model)
      self.notebook.add(self.config_tab_view.frame, text='Config')

      self.request_tab_view = Posty.RequestTabView(self.notebook, view_model)
      self.notebook.add(self.request_tab_view.frame, text='Request')

      self.response_tab_view = Posty.ResponseTabView(self.notebook, view_model)
      self.notebook.add(self.response_tab_view.frame, text='Response')

  def __init__(self):
    self.root = tk.Tk()
    self.root.title('Posty')

    self.view_model = ViewModel()

    self.view = Posty.MainView(self.root, self.view_model)

  def run(self):
    self.root.mainloop()


def main():
  posty = Posty()

  posty.run()

if __name__ == '__main__':
  main()