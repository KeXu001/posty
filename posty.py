
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class TextArea(tk.Text):
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

class ConfigView:
  def __init__(self, config_tab, view_model):
    # form

    self.form_view = tk.Frame(config_tab)
    self.form_view.grid_rowconfigure(0, weight=0) # verify
    self.form_view.grid_rowconfigure(1, weight=0) # CA cert
    self.form_view.grid_rowconfigure(2, weight=0) # client cert
    self.form_view.grid_rowconfigure(3, weight=0) # client key
    self.form_view.grid_columnconfigure(0, weight=0)
    self.form_view.grid_columnconfigure(1, weight=1)
    self.form_view.pack(expand=1, fill='both', padx=5, pady=5)

    padding = {
      'padx': 5,
      'pady': 5
    }

    # verify

    self.verify_lbl = tk.Label(self.form_view, text='Verify')
    self.verify_lbl.grid(row=0, column=0, sticky='w', **padding)

    self.verify = tk.Checkbutton(self.form_view, variable=view_model.config_verify)
    self.verify.grid(row=0, column=1, sticky='w', **padding)

    # ca_cert

    self.ca_cert_lbl = tk.Label(self.form_view, text='CA Cert/Bundle')
    self.ca_cert_lbl.grid(row=1, column=0, sticky='w', **padding)

    self.ca_cert_frame = tk.Frame(self.form_view)
    self.ca_cert_frame.grid(row=1, column=1, sticky='nsew', **padding)

    self.ca_cert = tk.Entry(self.ca_cert_frame, textvariable=view_model.config_ca_cert)
    self.ca_cert.pack(expand=True, fill=tk.X, side=tk.LEFT)

    self.ca_cert_btn = tk.Button(self.ca_cert_frame, text='Browse', padx=0, pady=0, command=lambda: self.select_file(view_model.config_ca_cert))
    self.ca_cert_btn.pack(side=tk.RIGHT)

    # client_cert

    self.client_cert_lbl = tk.Label(self.form_view, text='Client Cert')
    self.client_cert_lbl.grid(row=2, column=0, sticky='w', **padding)

    self.client_cert_frame = tk.Frame(self.form_view)
    self.client_cert_frame.grid(row=2, column=1, sticky='nsew', **padding)

    self.client_cert = tk.Entry(self.client_cert_frame, textvariable=view_model.config_client_cert)
    self.client_cert.pack(expand=True, fill=tk.X, side=tk.LEFT)

    self.client_cert_btn = tk.Button(self.client_cert_frame, text='Browse', padx=0, pady=0, command=lambda: self.select_file(view_model.config_client_cert))
    self.client_cert_btn.pack(side=tk.RIGHT)

    # client_key

    self.client_key_lbl = tk.Label(self.form_view, text='Client Key')
    self.client_key_lbl.grid(row=3, column=0, sticky='w', **padding)

    self.client_key_frame = tk.Frame(self.form_view)
    self.client_key_frame.grid(row=3, column=1, sticky='nsew', **padding)

    self.client_key = tk.Entry(self.client_key_frame, textvariable=view_model.config_client_key)
    self.client_key.pack(expand=True, fill=tk.X, side=tk.LEFT)

    self.client_key_btn = tk.Button(self.client_key_frame, text='Browse', padx=0, pady=0, command=lambda: self.select_file(view_model.config_client_key))
    self.client_key_btn.pack(side=tk.RIGHT)

  def select_file(self, string_var):
    selected = filedialog.askopenfilename()

    if len(selected) > 0:
      string_var.set(selected)

class RequestView:
  def __init__(self, request_tab, view_model):
    # form

    self.form_view = tk.Frame(request_tab)
    self.form_view.grid_rowconfigure(0, weight=0)
    self.form_view.grid_rowconfigure(1, weight=0)
    self.form_view.grid_rowconfigure(2, weight=1)
    self.form_view.grid_rowconfigure(3, weight=1)
    self.form_view.grid_columnconfigure(0, weight=0)
    self.form_view.grid_columnconfigure(1, weight=1)
    self.form_view.pack(expand=1, fill='both', padx=5, pady=5)

    padding = {
      'padx': 5,
      'pady': 5
    }

    # method

    self.method_lbl = tk.Label(self.form_view, text='Method')
    self.method_lbl.grid(row=0, column=0, sticky='w', **padding)

    self.method = ttk.Combobox(self.form_view, textvariable=view_model.request_method, values=view_model.request_method_options)
    self.method.grid(row=0, column=1, sticky='w', **padding)

    # url

    self.url_lbl = tk.Label(self.form_view, text='URL')
    self.url_lbl.grid(row=1, column=0, sticky='w', **padding)

    self.url = tk.Entry(self.form_view, textvariable=view_model.request_url)
    self.url.grid(row=1, column=1, sticky='we', **padding)

    # headers

    self.headers_lbl = tk.Label(self.form_view, text='Headers')
    self.headers_lbl.grid(row=2, column=0, sticky='w', **padding)

    self.headers_frame = tk.Frame(self.form_view)
    self.headers_frame.grid(row=2, column=1, sticky='nsew', **padding)

    self.headers_scroll = tk.Scrollbar(self.headers_frame, takefocus=False)
    self.headers_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.headers = TextArea(self.headers_frame, height=10, spacing1=10, textvariable=view_model.request_headers, yscrollcommand=self.headers_scroll.set)
    self.headers.pack(expand=True, fill=tk.BOTH)

    self.headers_scroll.config(command=self.headers.yview)

    # body

    self.body_lbl = tk.Label(self.form_view, text='Body')
    self.body_lbl.grid(row=3, column=0, sticky='w', **padding)

    self.body_frame = tk.Frame(self.form_view)
    self.body_frame.grid(row=3, column=1, sticky='nsew', **padding)

    self.body_scroll = tk.Scrollbar(self.body_frame, takefocus=False)
    self.body_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.body = TextArea(self.body_frame, height=10, spacing1=10, textvariable=view_model.request_body, yscrollcommand=self.body_scroll.set)
    self.body.pack(expand=True, fill=tk.BOTH)

    self.body_scroll.config(command=self.body.yview)

class ResponseView:
  def __init__(self, response_tab, view_model):
    # form

    self.form_view = tk.Frame(response_tab)
    self.form_view.grid_rowconfigure(0, weight=0)
    self.form_view.grid_rowconfigure(1, weight=0)
    self.form_view.grid_rowconfigure(2, weight=1)
    self.form_view.grid_rowconfigure(3, weight=1)
    self.form_view.grid_columnconfigure(0, weight=0)
    self.form_view.grid_columnconfigure(1, weight=1)
    self.form_view.pack(expand=1, fill='both', padx=5, pady=5)

    padding = {
      'padx': 5,
      'pady': 5
    }

    # go

    self.go_btn = ttk.Button(self.form_view, text='Go', command=lambda: self.go(view_model))
    self.go_btn.grid(row=0, column=1, sticky='w', **padding)

    # status

    self.status_lbl = tk.Label(self.form_view, text='Status')
    self.status_lbl.grid(row=1, column=0, sticky='w', **padding)

    self.status = ttk.Entry(self.form_view, textvariable=view_model.response_status)
    self.status.grid(row=1, column=1, sticky='w', **padding)

    # headers

    self.headers_lbl = tk.Label(self.form_view, text='Headers')
    self.headers_lbl.grid(row=2, column=0, sticky='w', **padding)

    self.headers_frame = tk.Frame(self.form_view)
    self.headers_frame.grid(row=2, column=1, sticky='nsew', **padding)

    self.headers_scroll = tk.Scrollbar(self.headers_frame, takefocus=False)
    self.headers_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.headers = TextArea(self.headers_frame, textvariable=view_model.response_headers, height=10, spacing1=10, yscrollcommand=self.headers_scroll.set)
    self.headers.pack(expand=True, fill=tk.BOTH)

    self.headers_scroll.config(command=self.headers.yview)

    # body

    self.body_lbl = tk.Label(self.form_view, text='Body')
    self.body_lbl.grid(row=3, column=0, sticky='w', **padding)

    self.body_frame = tk.Frame(self.form_view)
    self.body_frame.grid(row=3, column=1, sticky='nsew', **padding)

    self.body_scroll = tk.Scrollbar(self.body_frame, takefocus=False)
    self.body_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.body = TextArea(self.body_frame, height=10, spacing1=10, textvariable=view_model.response_body, yscrollcommand=self.body_scroll.set)
    self.body.pack(expand=True, fill=tk.BOTH)

    self.body_scroll.config(command=self.body.yview)

  def go(self, view_model):
    method = view_model.request_method.get().upper()

    url = view_model.request_url.get()

    headers = dict()
    for line in view_model.request_headers.get().split('\n'):
      if len(line) == 0:
        continue

      parts = line.split(':')
      if len(parts) == 2:
        key = parts[0].strip()
        value = parts[1].strip()

        headers[key] = value
      else:
        raise ValueError('Bad syntax for headers')

    data = view_model.request_body.get()

    prep_args = dict()

    if view_model.config_verify.get():
      if view_model.config_ca_cert.get():
        prep_args['verify'] = view_model.config_ca_cert.get()
      else:
        prep_args['verify'] = True

      if not url.startswith('https://'):
        raise ValueError('URL must start with https:// if configured to Verify')
    else:
      prep_args['verify'] = False

    client_cert = view_model.config_client_cert.get()
    client_key = view_model.config_client_key.get()
    if client_cert and client_key:
      prep_args['cert'] = (client_cert, client_key)
    elif client_cert and not client_key:
      raise ValueError('Must provide Client Key if providing Client Cert')
    elif not client_cert and client_key:
      raise ValueError('Most provide Client Cert if providing Client Key')

    # clear response

    view_model.response_status.set('')
    view_model.response_headers.set('')
    view_model.response_body.set('')

    sess = requests.Session()
    req = requests.Request(method=method, url=url, headers=headers, data=data)
    prepped = sess.prepare_request(req)

    resp = sess.send(prepped, **prep_args)

    view_model.response_status.set(str(resp.status_code))
    view_model.response_headers.set('\n'.join(k + ': ' + v for k,v in resp.headers.items()))
    view_model.response_body.set(resp.text)

class View:
  def __init__(self, root, view_model):
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(expand=True, fill='both')

    self.config_tab = tk.Frame(self.notebook)
    self.notebook.add(self.config_tab, text='Config')
    
    self.request_tab = tk.Frame(self.notebook)
    self.notebook.add(self.request_tab, text='Request')

    self.response_tab = tk.Frame(self.notebook)
    self.notebook.add(self.response_tab, text='Response')

    self.config_view = ConfigView(self.config_tab, view_model)

    self.request_view = RequestView(self.request_tab, view_model)
    
    self.response_view = ResponseView(self.response_tab, view_model)

class Posty:
  def __init__(self):
    self.root = tk.Tk()
    self.root.title('Posty')

    self.view_model = ViewModel()

    self.view = View(self.root, self.view_model)

    # Request Tab
      # headers
      # url
      # query parameters
      # body

    # Send Button

    # Response Tab
      # headers
      # body

    # Statistics Panel
      # time elapsed
    pass

  def run(self):
    self.root.mainloop()


def main():
  posty = Posty()

  posty.run()

if __name__ == '__main__':
  main()