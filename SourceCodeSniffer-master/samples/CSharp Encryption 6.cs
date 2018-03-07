using System;
using System.Windows.Forms;
using System.Security.Cryptography;

namespace ExampleCrypto
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            string strOriginalData = string.Empty;
            string strEncryptedData = string.Empty;
            string strDecryptedData = string.Empty;

            strOriginalData = "this is original data 1234567890"; // your original data in here
            MessageBox.Show("ORIGINAL DATA:\r\n" + strOriginalData);

            clsCrypto aes = new clsCrypto();
            aes.IV = "this is your IV";     // your IV
            aes.KEY = "this is your KEY";    // your KEY
            strEncryptedData = aes.Encrypt(strOriginalData, CipherMode.CBC);    // your cipher mode
            MessageBox.Show("ENCRYPTED DATA:\r\n" + strEncryptedData);

            strDecryptedData = aes.Decrypt(strEncryptedData, CipherMode.CBC);
            MessageBox.Show("DECRYPTED DATA:\r\n" + strDecryptedData);
        }

    }
}
2.Create clsCrypto.cs and copy paste follows code in your class and run your code. I used MD5 to generated Initial Vector(IV) and KEY of AES.

using System;
using System.Security.Cryptography;
using System.Text;
using System.Windows.Forms;
using System.IO;
using System.Runtime.Remoting.Metadata.W3cXsd2001;

namespace ExampleCrypto
{
    public class clsCrypto
    {
        private string _KEY = string.Empty;
        protected internal string KEY
        {
            get
            {
                return _KEY;
            }
            set
            {
                if (!string.IsNullOrEmpty(value))
                {
                    _KEY = value;
                }
            }
        }

        private string _IV = string.Empty;
        protected internal string IV
        {
            get
            {
                return _IV;
            }
            set
            {
                if (!string.IsNullOrEmpty(value))
                {
                    _IV = value;
                }
            }
        }

        private string CalcMD5(string strInput)
        {
            string strOutput = string.Empty;
            if (!string.IsNullOrEmpty(strInput))
            {
                try
                {
                    StringBuilder strHex = new StringBuilder();
                    using (MD5 md5 = MD5.Create())
                    {
                        byte[] bytArText = Encoding.Default.GetBytes(strInput);
                        byte[] bytArHash = md5.ComputeHash(bytArText);
                        for (int i = 0; i < bytArHash.Length; i++)
                        {
                            strHex.Append(bytArHash[i].ToString("X2"));
                        }
                        strOutput = strHex.ToString();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            return strOutput;
        }

        private byte[] GetBytesFromHexString(string strInput)
        {
            byte[] bytArOutput = new byte[] { };
            if ((!string.IsNullOrEmpty(strInput)) && strInput.Length % 2 == 0)
            {
                SoapHexBinary hexBinary = null;
                try
                {
                    hexBinary = SoapHexBinary.Parse(strInput);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                bytArOutput = hexBinary.Value;
            }
            return bytArOutput;
        }

        private byte[] GenerateIV()
        {
            byte[] bytArOutput = new byte[] { };
            try
            {
                string strIV = CalcMD5(IV);
                bytArOutput = GetBytesFromHexString(strIV);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            return bytArOutput;
        }

        private byte[] GenerateKey()
        {
            byte[] bytArOutput = new byte[] { };
            try
            {
                string strKey = CalcMD5(KEY);
                bytArOutput = GetBytesFromHexString(strKey);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            return bytArOutput;
        }

        protected internal string Encrypt(string strInput, CipherMode cipherMode)
        {
            string strOutput = string.Empty;
            if (!string.IsNullOrEmpty(strInput))
            {
                try
                {
                    byte[] bytePlainText = Encoding.Default.GetBytes(strInput);
                    using (RijndaelManaged rijManaged = new RijndaelManaged())
                    {
                        rijManaged.Mode = cipherMode;
                        rijManaged.BlockSize = 128;
                        rijManaged.KeySize = 128;
                        rijManaged.IV = GenerateIV();
                        rijManaged.Key = GenerateKey();
                        rijManaged.Padding = PaddingMode.Zeros;
                        ICryptoTransform icpoTransform = rijManaged.CreateEncryptor(rijManaged.Key, rijManaged.IV);
                        using (MemoryStream memStream = new MemoryStream())
                        {
                            using (CryptoStream cpoStream = new CryptoStream(memStream, icpoTransform, CryptoStreamMode.Write))
                            {
                                cpoStream.Write(bytePlainText, 0, bytePlainText.Length);
                                cpoStream.FlushFinalBlock();
                            }
                            strOutput = Encoding.Default.GetString(memStream.ToArray());
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            return strOutput;
        }

        protected internal string Decrypt(string strInput, CipherMode cipherMode)
        {
            string strOutput = string.Empty;
            if (!string.IsNullOrEmpty(strInput))
            {
                try
                {
                    byte[] byteCipherText = Encoding.Default.GetBytes(strInput);
                    byte[] byteBuffer = new byte[strInput.Length];
                    using (RijndaelManaged rijManaged = new RijndaelManaged())
                    {
                        rijManaged.Mode = cipherMode;
                        rijManaged.BlockSize = 128;
                        rijManaged.KeySize = 128;
                        rijManaged.IV = GenerateIV();
                        rijManaged.Key = GenerateKey();
                        rijManaged.Padding = PaddingMode.Zeros;
                        ICryptoTransform icpoTransform = rijManaged.CreateDecryptor(rijManaged.Key, rijManaged.IV);
                        using (MemoryStream memStream = new MemoryStream(byteCipherText))
                        {
                            using (CryptoStream cpoStream = new CryptoStream(memStream, icpoTransform, CryptoStreamMode.Read))
                            {
                                cpoStream.Read(byteBuffer, 0, byteBuffer.Length);
                            }
                            strOutput = Encoding.Default.GetString(byteBuffer);
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            return strOutput;
        }

    }
}