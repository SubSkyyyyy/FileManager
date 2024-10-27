from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 密钥（16字节，因为是AES-128）
key = b'931eca0d9370cc8c'

# 待解密的数据（确保是16字节的倍数，如果是加密时使用了padding）
encrypted_data = b'your_encrypted_data_here'

# 初始化AES解密器，这里使用的是ECB模式
cipher = AES.new(key, AES.MODE_CBC)

# ECB CBC CFB OFB CTR GCM

# 解密数据
decrypted_data = cipher.decrypt(encrypted_data)

# 如果加密时使用了padding，需要去除padding
try:
    decrypted_data = unpad(decrypted_data, AES.block_size)
except ValueError:
    print("Incorrect decryption")

# 输出解密后的数据
print(decrypted_data)