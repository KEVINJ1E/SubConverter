import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import requests
import base64
import yaml
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class SubConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("订阅解析与 VLESS 转换工具")
        self.root.geometry("1100x800")
        
        self.setup_ui()

    def setup_ui(self):
        # --- 顶部：URL输入区 ---
        top_frame = tk.Frame(self.root, pady=10, padx=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="订阅地址:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.start_btn = tk.Button(top_frame, text="开始解析", command=self.start_processing, bg="#4CAF50", fg="white")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # --- 中部：数据展示区 (分成左右两块) ---
        middle_frame = tk.Frame(self.root, padx=10)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：VLESS 节点链接
        vless_frame = tk.Frame(middle_frame)
        vless_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(vless_frame, text="VLESS 节点链接 (vless://)", font=("Arial", 10, "bold")).pack(anchor="w")
        self.vless_text = scrolledtext.ScrolledText(vless_frame, wrap=tk.WORD)
        self.vless_text.pack(fill=tk.BOTH, expand=True)

        # 右侧：Clash YAML 格式的 Proxies
        yaml_frame = tk.Frame(middle_frame)
        yaml_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(yaml_frame, text="Clash YAML 节点信息", font=("Arial", 10, "bold")).pack(anchor="w")
        self.yaml_text = scrolledtext.ScrolledText(yaml_frame, wrap=tk.WORD)
        self.yaml_text.pack(fill=tk.BOTH, expand=True)

        # --- 底部：日志展示区 ---
        bottom_frame = tk.Frame(self.root, pady=10, padx=10)
        bottom_frame.pack(fill=tk.X)
        tk.Label(bottom_frame, text="运行日志", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(bottom_frame, height=10, bg="#f4f4f4")
        self.log_text.pack(fill=tk.X)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def clear_ui(self):
        self.vless_text.delete(1.0, tk.END)
        self.yaml_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)

    def start_processing(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入订阅地址")
            return
        
        self.clear_ui()
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.process_subscription, args=(url,), daemon=True).start()

    def fix_base64_padding(self, s):
        if isinstance(s, str):
            return s + '=' * (-len(s) % 4)
        return s + b'=' * (-len(s) % 4)

    def process_subscription(self, url):
        try:
            # ==========================================
            # 步骤 1：请求订阅地址
            # ==========================================
            self.log("[-] 步骤1: 正在请求订阅地址...")
            headers = {
                'User-Agent': 'NetFlow/v3.0.6 clash-verge Platform/android'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            encrypted_content = response.text.strip()
            self.log(f"[+] 成功获取订阅数据，长度: {len(encrypted_content)} 字节")

            # ==========================================
            # 步骤 2：AES-128-CBC 解密
            # ==========================================
            self.log("[-] 步骤2: 进行 AES-128-CBC 解密...")
            key_hex = "62363232343431653466633437393434"
            iv_hex = "32366265363937336563396432663630"
            
            key = bytes.fromhex(key_hex)
            iv = bytes.fromhex(iv_hex)
            
            raw_ciphertext = base64.b64decode(self.fix_base64_padding(encrypted_content))
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(raw_ciphertext), AES.block_size)
            self.log("[+] AES 解密成功")

            # ==========================================
            # 步骤 3：进行 Base64 解码
            # ==========================================
            self.log("[-] 步骤3: 进行 Base64 解码...")
            yaml_bytes = base64.b64decode(self.fix_base64_padding(decrypted_bytes))
            yaml_str = yaml_bytes.decode('utf-8')
            self.log("[+] Base64 解码成功")

            # ==========================================
            # 步骤 4：提取并按照规范格式化 proxies
            # ==========================================
            self.log("[-] 步骤4: 按照完善规范重组 YAML 节点...")
            config_data = yaml.safe_load(yaml_str)
            proxies = config_data.get('proxies', [])
            
            if not proxies:
                self.log("[!] 警告: 未能在订阅中找到 proxies 节点数据")
                return

            self.log(f"[+] 成功提取到 {len(proxies)} 个节点，正在注入优化参数并重组...")

            # 参照第一个示例定义严格的输出顺序
            desired_order = [
                'name', 'server', 'port', 'client-fingerprint', 'flow', 
                'network', 'servername', 'tls', 'type', 'udp', 'uuid', 
                'xudp', 'skip-cert-verify', 'tfo'
            ]

            yaml_lines = ["proxies:"]
            for p in proxies:
                # 自动为 vless 节点补全高级优化参数
                if p.get('type') == 'vless':
                    p.setdefault('client-fingerprint', 'chrome')
                    p.setdefault('xudp', True)
                    p.setdefault('tfo', True)
                    p.setdefault('skip-cert-verify', True) # 依照示例同样补全

                # 按照严格顺序构建新的字典
                ordered_p = {}
                # 1. 优先按照期望列表排序提取
                for k in desired_order:
                    if k in p:
                        ordered_p[k] = p[k]
                
                # 2. 如果原始节点有不在这列表里的其他参数，追加在末尾
                for k in p:
                    if k not in desired_order:
                        ordered_p[k] = p[k]

                # 生成严格单行格式，sort_keys=False 保留我们定制的顺序
                p_str = yaml.dump(ordered_p, allow_unicode=True, sort_keys=False, default_flow_style=True, width=1000).strip()
                yaml_lines.append(f"  - {p_str}")
            
            yaml_output = "\n".join(yaml_lines) + "\n"
            self.yaml_text.insert(tk.END, yaml_output)

            # ==========================================
            # 步骤 5：转换为 vless:// 链接
            # ==========================================
            self.log("[-] 步骤5: 开始转换 VLESS 节点...")
            vless_links = []
            for p in proxies:
                if p.get('type') == 'vless':
                    link = self.convert_clash_vless_to_url(p)
                    vless_links.append(link)
            
            if vless_links:
                self.vless_text.insert(tk.END, "\n".join(vless_links) + "\n")
                self.log(f"[+] 转换完成，共生成 {len(vless_links)} 个 vless:// 链接")
            else:
                self.vless_text.insert(tk.END, "未在此配置中找到 VLESS 协议节点。\n")
                self.log("[!] 配置中没有发现 VLESS 节点。")

        except Exception as e:
            self.log(f"[X] 发生错误: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.start_btn.config(state=tk.NORMAL)

    def convert_clash_vless_to_url(self, proxy):
        name = urllib.parse.quote(proxy.get('name', 'Unknown'))
        server = proxy.get('server', '')
        port = proxy.get('port', '')
        uuid = proxy.get('uuid', '')
        
        params = {}
        params['type'] = proxy.get('network', 'tcp')
        
        if proxy.get('tls'):
            params['security'] = 'tls'
            if proxy.get('servername'):
                params['sni'] = proxy.get('servername')
            elif proxy.get('sni'):
                params['sni'] = proxy.get('sni')
            if proxy.get('client-fingerprint'):
                params['fp'] = proxy.get('client-fingerprint')
            if proxy.get('alpn'):
                alpn = proxy.get('alpn')
                if isinstance(alpn, list):
                    params['alpn'] = ','.join(alpn)
                else:
                    params['alpn'] = alpn
                    
        elif proxy.get('reality-opts'):
            params['security'] = 'reality'
            ro = proxy.get('reality-opts', {})
            params['pbk'] = ro.get('public-key', '')
            if 'short-id' in ro:
                params['sid'] = ro.get('short-id')
            if proxy.get('servername'):
                params['sni'] = proxy.get('servername')
            elif proxy.get('sni'):
                params['sni'] = proxy.get('sni')
            if proxy.get('client-fingerprint'):
                params['fp'] = proxy.get('client-fingerprint')
        else:
            params['security'] = 'none'

        if params['type'] == 'ws':
            ws_opts = proxy.get('ws-opts', {})
            params['path'] = ws_opts.get('path', '/')
            headers = ws_opts.get('headers', {})
            if 'Host' in headers:
                params['host'] = headers['Host']
                
        elif params['type'] == 'grpc':
            grpc_opts = proxy.get('grpc-opts', {})
            params['serviceName'] = grpc_opts.get('grpc-service-name', '')

        if proxy.get('flow'):
            params['flow'] = proxy.get('flow')
            
        query_string = urllib.parse.urlencode(params)
        vless_url = f"vless://{uuid}@{server}:{port}?{query_string}#{name}"
        return vless_url

if __name__ == "__main__":
    root = tk.Tk()
    app = SubConverterApp(root)
    root.mainloop()
