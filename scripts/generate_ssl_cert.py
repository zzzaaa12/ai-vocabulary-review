#!/usr/bin/env python3
"""
SSL Certificate Generation Script
Generates self-signed SSL certificates for development/testing purposes.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_openssl():
    """Check if OpenSSL is available."""
    try:
        result = subprocess.run(['openssl', 'version'],
                              capture_output=True, text=True, check=True)
        print(f"✓ OpenSSL 已找到: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 錯誤: 找不到 OpenSSL")
        print("請安裝 OpenSSL:")
        print("  Windows: https://slproweb.com/products/Win32OpenSSL.html")
        print("  Linux: sudo apt-get install openssl")
        print("  macOS: brew install openssl")
        return False


def generate_ssl_certificate(cert_dir, domain="localhost", days=365, key_size=2048):
    """
    Generate self-signed SSL certificate.

    Args:
        cert_dir: Directory to save certificates
        domain: Domain name for the certificate
        days: Certificate validity in days
        key_size: RSA key size
    """
    cert_dir = Path(cert_dir)
    cert_dir.mkdir(exist_ok=True)

    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"

    # Certificate subject
    subject = f"/C=TW/ST=Taiwan/L=Taipei/O=Development/OU=IT/CN={domain}"

    print(f"🔧 正在生成 SSL 憑證...")
    print(f"📁 憑證目錄: {cert_dir.absolute()}")
    print(f"🌐 域名: {domain}")
    print(f"📅 有效期: {days} 天")
    print(f"🔑 金鑰大小: {key_size} bits")

    try:
        # Generate private key and certificate in one command
        cmd = [
            'openssl', 'req', '-x509', '-newkey', f'rsa:{key_size}',
            '-keyout', str(key_file),
            '-out', str(cert_file),
            '-days', str(days),
            '-nodes',  # No passphrase
            '-subj', subject
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        print("✅ SSL 憑證生成成功!")
        print(f"📜 憑證檔案: {cert_file}")
        print(f"🔐 私鑰檔案: {key_file}")

        # Set appropriate permissions on Unix-like systems
        if os.name != 'nt':
            os.chmod(key_file, 0o600)  # Read only for owner
            os.chmod(cert_file, 0o644)  # Read for all, write for owner
            print("✓ 檔案權限已設定")

        # Display certificate info
        print("\n📋 憑證資訊:")
        try:
            result = subprocess.run(['openssl', 'x509', '-in', str(cert_file),
                                   '-text', '-noout'],
                                  capture_output=True, text=True, check=True)

            # Extract relevant info
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Not Before:' in line or 'Not After:' in line or 'Subject:' in line:
                    print(f"  {line.strip()}")

        except subprocess.CalledProcessError:
            print("  無法顯示憑證詳細資訊")

        print("\n⚠️  注意事項:")
        print("- 這是自簽名憑證，瀏覽器會顯示安全警告")
        print("- 僅適用於開發和測試環境")
        print("- 生產環境請使用受信任的 CA 憑證")
        print("- 請勿將私鑰檔案提交到版本控制系統")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 憑證生成失敗: {e}")
        if e.stderr:
            print(f"錯誤詳情: {e.stderr.decode()}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="生成自簽名 SSL 憑證",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python generate_ssl_cert.py                    # 使用預設設定
  python generate_ssl_cert.py -d example.com     # 指定域名
  python generate_ssl_cert.py -o ../certificates # 指定輸出目錄
  python generate_ssl_cert.py --days 730         # 設定2年有效期
        """
    )

    parser.add_argument('-o', '--output',
                       default='certs',
                       help='憑證輸出目錄 (預設: certs)')

    parser.add_argument('-d', '--domain',
                       default='localhost',
                       help='憑證域名 (預設: localhost)')

    parser.add_argument('--days',
                       type=int,
                       default=365,
                       help='憑證有效天數 (預設: 365)')

    parser.add_argument('--key-size',
                       type=int,
                       default=2048,
                       choices=[1024, 2048, 4096],
                       help='RSA 金鑰大小 (預設: 2048)')

    parser.add_argument('--force',
                       action='store_true',
                       help='強制覆蓋現有憑證')

    args = parser.parse_args()

    print("🔒 SSL 憑證生成工具")
    print("=" * 40)

    # Check if OpenSSL is available
    if not check_openssl():
        sys.exit(1)

    # Check if certificates already exist
    cert_dir = Path(args.output)
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"

    if (cert_file.exists() or key_file.exists()) and not args.force:
        print(f"⚠️  憑證檔案已存在於 {cert_dir}")
        response = input("是否要覆蓋現有憑證? (y/N): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("❌ 操作已取消")
            sys.exit(0)

    # Generate certificate
    success = generate_ssl_certificate(
        cert_dir=args.output,
        domain=args.domain,
        days=args.days,
        key_size=args.key_size
    )

    if success:
        print("\n🎉 憑證生成完成!")
        print(f"現在可以在應用程式中使用 HTTPS 功能")
        print(f"伺服器啟動後請訪問: https://{args.domain}:8080")
        sys.exit(0)
    else:
        print("❌ 憑證生成失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()