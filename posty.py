
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json

class FilepathEntry(tk.Frame):
  def __init__(self, parent, textvariable=None, save_as=False, *args, **kwargs):
    super(FilepathEntry, self).__init__(parent)

    self.text_var = textvariable
    self.save_as = save_as

    self.entry = tk.Entry(self, textvariable=self.text_var)
    self.entry.pack(expand=True, fill=tk.X, side=tk.LEFT)

    self.button = tk.Button(self, text='Browse', padx=0, pady=0, command=self.on_button_press)
    self.button.pack(side=tk.RIGHT)

  def on_button_press(self):
    if self.save_as:
      selected = filedialog.asksaveasfilename()
    else:
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

class Posty:

  class TabView:
    padding = {
      'padx': 5,
      'pady': 5
    }

    def __init__(self, parent):
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
    def __init__(self, parent, mc):
      super(Posty.ConfigTabView, self).__init__(parent)

      self.add_item(0, 'Verify',
        lambda parent: tk.Checkbutton(parent, variable=mc.model['config']['verify']),
        sticky='w')

      self.add_item(0, 'CA Cert',
        lambda parent: FilepathEntry(parent, textvariable=mc.model['config']['ca_cert']),
        sticky='ew')

      self.add_item(0, 'Client Cert',
        lambda parent: FilepathEntry(parent, textvariable=mc.model['config']['client_cert']),
        sticky='ew')

      self.add_item(0, 'Client Key',
        lambda parent: FilepathEntry(parent, textvariable=mc.model['config']['client_key']),
        sticky='ew')

      self.add_item(0, 'Defaults File',
        lambda parent: FilepathEntry(parent, textvariable=mc.model['config']['defaults_file'], save_as=True),
        sticky='ew')

      self.add_item(0, 'Load Defaults',
        lambda parent: ttk.Button(parent, text='Load', command=mc.load_defaults),
        sticky='w')

      self.add_item(0, 'Save Defaults',
        lambda parent: ttk.Button(parent, text='Save', command=mc.save_defaults),
        sticky='w')

  class RequestTabView(TabView):
    def __init__(self, parent, mc):
      super(Posty.RequestTabView, self).__init__(parent)

      self.add_item(0, 'Method',
        lambda parent: ttk.Combobox(parent, textvariable=mc.model['request']['method'], values=['GET','POST','PUT','DELETE']),
        sticky='w')

      self.add_item(0, 'URL',
        lambda parent: tk.Entry(parent, textvariable=mc.model['request']['url']),
        sticky='ew')

      self.add_item(0, 'Headers',
        lambda parent: ScrollableTextArea(parent, textvariable=mc.model['request']['headers'], height=8, spacing1=8),
        sticky='nsew')

      self.add_item(0, 'Body',
        lambda parent: ScrollableTextArea(parent, textvariable=mc.model['request']['body'], height=8, spacing1=8),
        sticky='nsew')

  class ResponseTabView(TabView):
    def __init__(self, parent, mc):
      super(Posty.ResponseTabView, self).__init__(parent)

      self.add_item(0, 'Request',
        lambda parent: ttk.Button(parent, text='Send', command=mc.go),
        sticky='w')

      self.add_item(0, 'Status',
        lambda parent: tk.Entry(parent, textvariable=mc.model['response']['status']),
        sticky='ew')

      self.add_item(0, 'Headers',
        lambda parent: ScrollableTextArea(parent, textvariable=mc.model['response']['headers'], height=8, spacing1=8),
        sticky='nsew')

      self.add_item(0, 'Body',
        lambda parent: ScrollableTextArea(parent, textvariable=mc.model['response']['body'], height=8, spacing1=8),
        sticky='nsew')

  class MainView:
    def __init__(self, root, mc):
      self.notebook = ttk.Notebook(root)
      self.notebook.pack(expand=True, fill='both')

      self.config_tab_view = Posty.ConfigTabView(self.notebook, mc)
      self.notebook.add(self.config_tab_view.frame, text='Config')

      self.request_tab_view = Posty.RequestTabView(self.notebook, mc)
      self.notebook.add(self.request_tab_view.frame, text='Request')

      self.response_tab_view = Posty.ResponseTabView(self.notebook, mc)
      self.notebook.add(self.response_tab_view.frame, text='Response')

  class ModelController:
    def __init__(self):
      self.model = {
        'config': {
          'verify': tk.IntVar(),
          'ca_cert': tk.StringVar(),
          'client_cert': tk.StringVar(),
          'client_key': tk.StringVar(),
          'defaults_file': tk.StringVar()
        },
        'request': {
          'method': tk.StringVar(),
          'url': tk.StringVar(),
          'headers': tk.StringVar(),
          'body': tk.StringVar()
        },
        'response': {
          'status': tk.StringVar(),
          'headers': tk.StringVar(),
          'body': tk.StringVar()
        }
      }

      self.model['config']['verify'].set(1)

      self.defaultable_keys = [
        ('config', 'verify'),
        ('config', 'ca_cert'),
        ('config', 'client_cert'),
        ('config', 'client_key'),
        ('request', 'method'),
        ('request', 'url'),
        ('request', 'headers'),
        ('request', 'body')
      ]

    def go(self):
      method = self.model['request']['method'].get().upper()

      url = self.model['request']['url'].get()

      headers = dict()
      for line in self.model['request']['headers'].get().split('\n'):
        if len(line) == 0:
          continue

        parts = line.split(':')
        if len(parts) == 2:
          key = parts[0].strip()
          value = parts[1].strip()

          headers[key] = value
        else:
          raise ValueError('Bad syntax for headers')

      data = self.model['request']['body'].get()

      prep_args = dict()

      if self.model['config']['verify'].get():
        if self.model['config']['ca_cert'].get():
          prep_args['verify'] = self.model['config']['ca_cert'].get()
        else:
          prep_args['verify'] = True

        if not url.startswith('https://'):
          raise ValueError('URL must start with https:// if configured to Verify')
      else:
        prep_args['verify'] = False

      client_cert = self.model['config']['client_cert'].get()
      client_key = self.model['config']['client_key'].get()
      if client_cert and client_key:
        prep_args['cert'] = (client_cert, client_key)
      elif client_cert and not client_key:
        raise ValueError('Must provide Client Key if providing Client Cert')
      elif not client_cert and client_key:
        raise ValueError('Most provide Client Cert if providing Client Key')

      # clear response

      self.model['response']['status'].set('')
      self.model['response']['headers'].set('')
      self.model['response']['body'].set('')

      sess = requests.Session()
      req = requests.Request(method=method, url=url, headers=headers, data=data)
      prepped = sess.prepare_request(req)

      resp = sess.send(prepped, **prep_args)

      self.model['response']['status'].set(str(resp.status_code))
      self.model['response']['headers'].set('\n'.join(k + ': ' + v for k,v in resp.headers.items()))
      self.model['response']['body'].set(resp.text)

    def load_defaults(self):
      defaults_file = self.model['config']['defaults_file'].get()
      with open(defaults_file, 'r') as f:
        obj = f.read()

      defaults = json.loads(obj)

      self.model['config']['verify'].set(defaults['config']['verify'])
      self.model['config']['ca_cert'].set(defaults['config']['ca_cert'])
      self.model['config']['client_cert'].set(defaults['config']['client_cert'])
      self.model['config']['client_key'].set(defaults['config']['client_key'])
      self.model['request']['method'].set(defaults['request']['method'])
      self.model['request']['url'].set(defaults['request']['url'])
      self.model['request']['headers'].set(defaults['request']['headers'])
      self.model['request']['body'].set(defaults['request']['body'])

    def save_defaults(self):
      defaults = {
        'config': {
          'verify': self.model['config']['verify'].get(),
          'ca_cert': self.model['config']['ca_cert'].get(),
          'client_cert': self.model['config']['client_cert'].get(),
          'client_key': self.model['config']['client_key'].get()
        },
        'request': {
          'method': self.model['request']['method'].get(),
          'url': self.model['request']['url'].get(),
          'headers': self.model['request']['headers'].get(),
          'body': self.model['request']['body'].get()
        }
      }

      defaults_str = json.dumps(defaults)

      defaults_file = self.model['config']['defaults_file'].get()
      with open(defaults_file, 'w') as f:
        f.write(defaults_str)

  def __init__(self):
    self.root = tk.Tk()
    self.root.title('Posty')

    self.mc = Posty.ModelController()

    self.view = Posty.MainView(self.root, self.mc)

  def run(self):
    self.root.mainloop()


def main():
  posty = Posty()

  posty.run()

if __name__ == '__main__':
  main()