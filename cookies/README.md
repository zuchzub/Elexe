# **📜 Using Cookies**

### **🔹 Method: Netscape HTTP Cookie File**
To authenticate requests using browser cookies, follow these steps:

> [!IMPORTANT]
> - Always use a **secondary account** for generating cookies.
> - Once cookies are uploaded, **do not log in again** on that account. It may invalidate the session.

---

## **📌 Step 1: Export Cookies in Netscape Format**
Use a browser extension to export cookies as a **`cookies.txt`** file in **Netscape HTTP format**:

### **🌐 Recommended Extensions:**  
| Browser     | Extension         | Download Link                                                                                                      |  
|-------------|-------------------|--------------------------------------------------------------------------------------------------------------------|  
| **Chrome**  | `Get cookies.txt` | [Chrome Web Store](https://chromewebstore.google.com/detail/get-cookiestxt-clean/ahmnmhfbokciafffnknlekllgcnafnie) |  
| **Firefox** | `cookies.txt`     | [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)                                     |  

### **📥 How to Export:**
1. Install the extension.
2. Navigate to the YouTube.com in private/incognito tab and log in.
3. Play a video for 1 minute.
4. Click the extension icon and select **"Export cookies.txt"**.
5. Save the file.

---

## **📌 Step 2: Upload Cookies to a Paste Service**  
Host your `cookies.txt` on a text-sharing service:  

- **[BatBin](https://batbin.me)**

### **📤 Upload Steps:**  
1. Open the paste service.  
2. Copy-paste the **entire content** of `cookies.txt`.  
3. Click **"Create Paste"** and copy the URL.  

---

## **📌 Step 3: Set the Environment Variable**  
Add the paste URL to your **`COOKIES`** environment variable.  

### **⚙️ Example:**  
```env
COOKIES=https://batbin.me/xyz012
```  

---

## **🎉 Enjoy using cookies!**
