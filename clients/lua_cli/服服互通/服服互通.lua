local omega = require("omega")
local json = require("json")
local crypto = require("crypto")

package.path = ("%s;%s"):format(
    package.path,
    omega.storage_path.get_code_path("LuaLoader", "?.lua")
)

local coromega = require("coromega").from(omega)

local version = coromega.config.Version

-- local conn_ipaddr = coromega.config["连接"]
-- ServerLink : SuperLink

local cfg = coromega.config

local is_conn = false
local ip_enabled = true
local need_con = true
local con_ip = cfg["互通中心服务器IP"]
local protocol = cfg["互通协议(目前不能更改)"]
local enable_chat_in = cfg["是否允许转发互通频道的聊天消息到服内"]
local enable_chat_out = cfg["是否允许转发服内的聊天消息到互通频道"]
local server_name = cfg["本服在频道显示的昵称"]
local channel_name = cfg["所在频道名"]
local channel_token = cfg["所在频道密码"]
-- formats
local chat_in_fmt = cfg["消息格式"]["来自互通频道的聊天消息"]
local server_join_fmt = cfg["消息格式"]["来自互通频道的客户端租赁服加入消息"]
local server_leave_fmt = cfg["消息格式"]["来自互通频道的客户端租赁服离开消息"]

---@param type string
---@param content table
---@param uuid? string
local function format_data(type, content, uuid)
    uuid = uuid or nil
    if uuid ~= nil then
        content["UUID"] = uuid
    end
    return { Type = type, Content = content }
end

---@param t string
local function make_data(t)
    local t1 = json.decode(t)
    return format_data(t1.Type, t1.Content)
end

local function handler(data_msg)
    if data_msg == nil then
        coromega:print("§c服服互通: 与中心服务器断开连接, 尝试重连")
        is_conn = false
        coromega:start_new(Connector)
        return
    end
    local data = make_data(data_msg)
    local data_type = data.Type
    if data_type == "chat.msg" and enable_chat_in then
        coromega:say_to("@a",
            chat_in_fmt:gsub("[客户端名]", data.Content.Sender):gsub("[玩家名]", data.Content.ChatName):gsub("[消息]",
                data.Content.Msg))
    elseif data_type == "client.join" then
        coromega:say_to("@a", server_join_fmt:gsub("[客户端名]", data.Content.Name))
    elseif data_type == "client.leave" then
        coromega:say_to("@a", server_leave_fmt:gsub("[客户端名]", data.Content.Name))
    end
end

local function on_player_message(chat)
    local player, msg = chat.name, table.concat(chat.msg)
    if coromega:get_player(chat.name) == nil then
        return
    end
    if is_conn and enable_chat_out then
        WebSocketCli:send(format_data("chat.msg", { ChatName = player, Msg = msg }))
    end
end

function GetDefaultLinkIP()
    -- SuperLink
    local resp, err = coromega:http_request(
        "GET", "https://tdload.tblstudio.cn/raw.githubusercontent.com/ToolDelta/SuperLink/main/source.json")
    if err then
        coromega:print("§c服服互通: 无法获取互通协议: SuperLink协议 官方源")
        ip_enabled = false
    end
    local src = json.decode(resp.body)
    local ip_name = ""
    local ip_ip = ""
    for k, v in pairs(src) do
        ip_name = k
        ip_ip = v
        ip_enabled = true
        -- todo
        break
    end
    return ip_name, ip_ip
end

function Connector()
    coromega:sleep(1.0)
    if protocol ~= "SuperLink-v4@SuperScript" then
        coromega:print("§c目前只能使用 SuperLink-v4@SuperScript 作为服服互通协议!")
        coromega:print("§c已自动禁用 服服互通[lua]")
        return
    end
    local server_data = coromega:user_info()
    local headers = {
        Protocol = protocol,
        ServerName = crypto.base64_encode(server_name:gsub("[自动生成]", "租赁服" .. server_data.HashedServeCode.sub(0, 6))),
        ChannelName = crypto.base64_encode(channel_name),
        ChannelToken = crypto.base64_encode(channel_token)
    }
    local retry_time = -5
    while true do
        WebSocketCli = coromega:connect_to_websocket(con_ip, headers)
        if WebSocketCli ~= nil then
            break
        end
        if retry_time < 300 then
            retry_time = retry_time + 10
        end
        coromega:print(("§c服服互通 无法连接中心服务器, %ss后重试"):format(retry_time))
        coromega:sleep(retry_time)
    end
    -- ws handler
    is_conn = true
    WebSocketCli:when_new_msg(handler)
    local first_received = WebSocketCli:receive_message()
    local fdata = make_data(first_received)
    if fdata.Type == "server.auth_success" then
        coromega:print(("§a连接成功, 当前频道在线 %s 个服务器"):format(fdata.Content.Member_count))
    else
        coromega:print("§c服服互通连接失败: ", fdata.Content.Reason)
    end
end

local function main()
    if con_ip == "自动选择线路" then
        local ip_name, ip_ip = GetDefaultLinkIP()
        if ip_enabled then
            coromega:print("§6未指定中心服务器IP, 将自动使用线路: " .. ip_name)
            con_ip = ip_ip
        else
            coromega:print("§c服服互通: 自动获取可用线路失败, 插件将不予启用")
        end
    end
    if ip_enabled then
        Connector()
    end
end

if need_con then
    coromega:start_new(main)
end

coromega:when_chat_msg():start_new(on_player_message)

coromega:run()
