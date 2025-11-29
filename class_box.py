"""

    Discord 機器人
    此程式負責幫助主程式方便調取json的資料
    主程式 ---> [類別物件] ---> json
    製作人 : Danny0224
    2025 / 08 / 16

"""

#程式庫導入
import json
import datetime
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")    # 取得state資料夾的路徑
json_path = os.path.join(path, "current_box.json")                          # 存儲語音房資訊
register_owner_leave = os.path.join(path, "register_owner_leave.json")      # 登記目前離開語音房的擁有者

# 檢查state資料夾是否存在
if not os.path.exists(path):
    os.makedirs(path)  # 如果不存在，則創建資料夾

# 檢查json_path.json是否存在
if not os.path.exists(json_path):
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump({}, file, ensure_ascii=False, indent=4)  # 初始化語音房資訊檔案

# 檢查register_owner_leave.json是否存在
if not os.path.exists(register_owner_leave):
    with open(register_owner_leave, "w", encoding="utf-8") as file:
        data = {
            "currently_absent": []  # 初始化目前離開語音房的擁有者列表
        }
        json.dump(data, file, ensure_ascii=False, indent=4)  # 初始化擁有者離開語音房檔案

def load_data(): # 讀取Json檔案 (語音房資料)
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_data(data): # 寫入Json檔案 (語音房資料)
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_leave_owner_data():
    with open(register_owner_leave, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_leave_owner_data(data):
    with open(register_owner_leave, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

class app_box: #創建語音房
    def __init__(self, user_id: int, channel_id: int):

        self.exist = True # 頻道使否存在

        self.channel_id = channel_id     # 頻道ID
        self.owner = user_id             # 語音房擁有者
        self.quit_owner_time = None      # 擁有者離開語音房的時間
        self.permissions = []            # 擁有操作權的人
        self.blacklist = []              # 黑名單內的人
        self.overt = True                # 語音房是否為公開
        self.whitelist = []              # 白名單內的人

        # json檔格式
        channel_data = {
            str(channel_id): {
                "owner": self.owner,
                "quit_owner_time": self.quit_owner_time,
                "permissions": self.permissions,
                "blacklist": self.blacklist,
                "overt": self.overt,
                "whitelist": self.whitelist
            }
        }

        # 寫入到json檔
        data = load_data()
        data.update(channel_data)
        save_data(data)

    def renew(self): #更新資料

        data = load_data().get(str(self.channel_id))

        if data != None:
            self.exist = True                                   # 頻道使否存在

            self.channel_id = data.get("channel_id")            # 頻道ID
            self.owner = data.get("owner")                      # 語音房擁有者
            self.quit_owner_time = data.get("quit_owner_time")  # 擁有者離開語音房的時間
            self.permissions = data.get("permissions")          # 擁有操作權的人
            self.blacklist = data.get("blacklist")              # 黑名單內的人
            self.overt = data.get("overt")                      # 語音房是否為公開
            self.whitelist = data.get("whitelist")              # 白名單內的人
        else:
            self.exist = False                                  # 頻道使否存在

            self.channel_id = None                              # 頻道ID
            self.owner = None                                   # 語音房擁有者
            self.quit_owner_time = None                         # 擁有者離開語音房的時間
            self.permissions = None                             # 擁有操作權的人
            self.blacklist = None                               # 黑名單內的人
            self.overt = None                                   # 語音房是否為公開
            self.whitelist = None                               # 白名單內的人
            
    def delete(self): # 刪除語音房的Json檔的數據
        
        data = load_data()
        if data.get(str(self.channel_id)) != None: # 檢查包廂是否存在
            del data[str(self.channel_id)]
            save_data(data)

            self.renew() # 更新資料
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法刪除")
            return

    def add_permissions(self, member: int): # 新增權限

        data = load_data()
        if data != None:
            permissions: list = data.get(str(self.channel_id)).get("permissions")
            permissions.append(member)
            data.get(str(self.channel_id)).update({"permissions": permissions})

            save_data(data) # 儲存Json資料
            self.permissions = permissions
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 添加權限")
            return

    def delete_permissions(self, member: int): # 刪除權限

        data = load_data()
        if data != None:
            permissions: list = data.get(str(self.channel_id)).get("permissions")
            permissions.remove(member)
            data.get(str(self.channel_id)).update({"permissions": permissions})

            save_data(data) # 儲存Json資料
            self.permissions = permissions
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 刪除權限")
            return

    def add_blacklist(self, member: int): # 新增黑名單

        data = load_data()
        if data != None:
            channel_data = data.get(str(self.channel_id))
            if channel_data == None:
                print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 添加黑名單")
                return

            blacklist: list = channel_data.get("blacklist")
            blacklist.append(member)
            channel_data.update({"blacklist": blacklist})

            data.update({str(self.channel_id): channel_data})

            save_data(data) # 儲存Json資料
            self.blacklist = blacklist
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 添加黑名單")
            return

    def delete_blacklist(self, member: int): # 刪除黑名單

        data = load_data()
        if data != None:
            blacklist: list = data.get(str(self.channel_id)).get("blacklist")
            blacklist.remove(member)
            data.get(str(self.channel_id)).update({"blacklist": blacklist})

            save_data(data) # 儲存Json資料
            self.blacklist = blacklist
            return

        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 刪除黑名單")
            return

    def add_whitelist(self, member: int): # 新增白名單

        data = load_data()
        if data != None:
            whitelist: list = data.get(str(self.channel_id)).get("whitelist")
            whitelist.append(member)
            data.get(str(self.channel_id)).update({"whitelist": whitelist})

            save_data(data) # 儲存Json資料
            self.whitelist = whitelist
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 添加白名單")
            return

    def delete_whitelist(self, member: int): # 刪除白名單

        data = load_data()
        if data != None:
            whitelist: list = data.get(str(self.channel_id)).get("whitelist")
            whitelist.remove(member)
            data.get(str(self.channel_id)).update({"whitelist": whitelist})

            save_data(data) # 儲存Json資料
            self.whitelist = whitelist
            return

        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 刪除白名單")
            return

    def edit_owner(self, member: int): # 更改擁有者
        data = load_data()
        if data != None:
            data.get(str(self.channel_id)).update({"owner": member})

            save_data(data) # 儲存Json資料
            self.owner = member
            return
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法對 {member} 轉移語音房擁有者")
            return
        
    def edit_quit_owner_time(self, owner_return: bool): # 如果輸入True代表房主回來了，反之False為房主離開了

        data = load_data()
        register_data = load_leave_owner_data()
        register_list = register_data.get("currently_absent")
        if data != None: # 檢查語音房是否存在

            if owner_return == True:
                # 修改current_box.json的資料
                data.get(str(self.channel_id)).update({"quit_owner_time": None})
                save_data(data)

                # 修改register_owner_leave.json的資料
                if self.channel_id in register_list:
                    register_list.remove(self.channel_id)
                    register_data.update({"currently_absent": register_list})
                    save_leave_owner_data(register_data)
                    return
                else:
                    print(f"錯誤: {register_owner_leave} 資料中，沒有 {self.channel_id} 無法刪除語音房ID")
                    return
            
            else:
                # 修改current_box.json的資料
                data.get(str(self.channel_id)).update({"quit_owner_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                save_data(data) # 儲存Json資料

                # 修改register_owner_leave.json的資料
                if self.channel_id not in register_list:
                    register_list.append(self.channel_id)
                    register_data.update({"currently_absent": register_list})
                    save_leave_owner_data(register_data)
                    return
                else:
                    print(f"錯誤: {register_owner_leave} 資料中，已經存在 {self.channel_id} 添加包廂ID")
                    return

        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法更改擁有者離開的時間")
            return

    def have_permission(self, member: int): # 查看某位成員是否有操作權
        if self.exist: #查看頻道是否存在

            if member in self.permissions or member == self.owner:
                return True
            else:
                return False
        
        else:
            print(f"錯誤: {self.channel_id} 語音房不存在，無法查看 {member} 是否有操作權")
            return False
        
    def is_owner(self, member: int): # 查看某位成員是否為擁有者
        if self.exist: #查看頻道是否存在

            if member == self.owner:
                return True
            else:
                return False

class box_id(app_box):
    def __init__(self, channel_id: int): #指定語音房
        # 讀取資料
        data = load_data().get(str(channel_id))
        if data == None:
            self.exist = False # 頻道使否存在
        else:
            self.exist = True  # 頻道使否存在

            self.channel_id = channel_id                        # 頻道ID
            self.owner = data.get("owner")                      # 語音房擁有者
            self.quit_owner_time = data.get("quit_owner_time")  # 擁有者離開語音房的時間
            self.permissions = data.get("permissions")          # 擁有操作權的人
            self.blacklist = data.get("blacklist")              # 黑名單內的人
            self.overt = data.get("overt")                      # 語音房是否為公開
            self.whitelist = data.get("whitelist")              # 白名單內的人



def register_owner_leave_list(): 
    return load_leave_owner_data().get("currently_absent")

def all_box():
    return [int(i) for i in load_data()]