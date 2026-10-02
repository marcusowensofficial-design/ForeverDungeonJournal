local ADDON_NAME, FDJ = ...

-- Shared namespace for the addon. Each file receives the same addon table.
if type(FDJ) ~= "table" then
    FDJ = _G.ForeverDungeonJournal_NS or {}
end
_G.ForeverDungeonJournal_NS = FDJ

FDJ.ADDON_NAME = ADDON_NAME
FDJ.Constants = FDJ.Constants or {}
FDJ.Constants.ALBA_FAIRMOON_LOCATION = "Alba Fairmoon, Sentinel Hill inn, Westfall"
FDJ.WISHLIST_STAR_TEXTURE = "|TInterface\\AddOns\\ForeverDungeonJournal\\Media\\Star_Gold.tga:13:13:0:-1|t "

ForeverDungeonJournalDB = ForeverDungeonJournalDB or {}

-- Native WoW keybinding entry (Options > Keybindings > AddOns).

local bindingLocale = GetLocale and GetLocale() or "enUS"

local bindingHeaders = {
    deDE = "Forever Dungeonjournal",
    frFR = "Forever Journal des donjons",
    esES = "Forever Diario de mazmorras",
    esMX = "Forever Diario de mazmorras",
    itIT = "Forever Diario delle spedizioni",
    ptBR = "Forever Diário de masmorras",
    ruRU = "Forever Журнал подземелий",
    koKR = "Forever 던전 도감",
    zhCN = "Forever 地下城手册",
    zhTW = "Forever 地城手冊",
}
BINDING_HEADER_FOREVERDUNGEONJOURNAL = bindingHeaders[bindingLocale] or "Forever Dungeon Journal"

local bindingNames = {
    deDE = "Dungeonjournal öffnen/schließen",
    frFR = "Ouvrir/Fermer le journal des donjons",
    esES = "Abrir/Cerrar el diario de mazmorras",
    esMX = "Abrir/Cerrar el diario de mazmorras",
    itIT = "Apri/Chiudi il diario delle spedizioni",
    ptBR = "Abrir/Fechar o diário de masmorras",
    ruRU = "Открыть/Закрыть журнал подземелий",
    koKR = "던전 도감 열기/닫기",
    zhCN = "打开/关闭地下城手册",
    zhTW = "開啟/關閉地城手冊",
}
BINDING_NAME_FOREVERDUNGEONJOURNAL_TOGGLE = bindingNames[bindingLocale] or "Open/Close Dungeon Journal"

-- Security diagnostics: catch and report any Blizzard UI protected action blocks
FDJ.securityAlerts = FDJ.securityAlerts or {}
local securityWatcher = CreateFrame("Frame")
securityWatcher:RegisterEvent("ADDON_ACTION_FORBIDDEN")
securityWatcher:RegisterEvent("ADDON_ACTION_BLOCKED")
securityWatcher:RegisterEvent("PLAYER_ENTERING_WORLD")
securityWatcher:SetScript("OnEvent", function(self, event, addon, action)
    if event == "ADDON_ACTION_FORBIDDEN" or event == "ADDON_ACTION_BLOCKED" then
        if addon == ADDON_NAME or addon == "ForeverDungeonJournal" or addon == "Forever_Dungeon_Journal" then
            local alert = {
                event = tostring(event),
                addon = tostring(addon),
                action = tostring(action or "Unknown"),
            }
            table.insert(FDJ.securityAlerts, alert)
            ForeverDungeonJournalDB = ForeverDungeonJournalDB or {}
            ForeverDungeonJournalDB.lastSecurityAlert = alert
            local msg = string.format("|cffff2020[FDJ Security Alert]|r Event: |cffffff00%s|r | Blocked Action: |cff00ffff%s|r", alert.event, alert.action)
            if DEFAULT_CHAT_FRAME and DEFAULT_CHAT_FRAME.AddMessage then
                DEFAULT_CHAT_FRAME:AddMessage(msg)
            else
                print(msg)
            end
        end
    elseif event == "PLAYER_ENTERING_WORLD" then
        if #FDJ.securityAlerts > 0 and DEFAULT_CHAT_FRAME and DEFAULT_CHAT_FRAME.AddMessage then
            for _, alert in ipairs(FDJ.securityAlerts) do
                DEFAULT_CHAT_FRAME:AddMessage(string.format("|cffff2020[FDJ Security Alert on Load]|r %s: |cffffff00%s|r", alert.event, alert.action))
            end
        end
    end
end)

-- ============================================================
-- LIVE DEFEAT TRACKER (In-Memory Session State)
-- ============================================================
FDJ.defeatedBosses = {}
FDJ.bossByNpcID = {}
FDJ.bossByName = {}

function FDJ.BuildBossLookups()
    if not FDJ.DB or not FDJ.ORDER then return end
    for _, dungeonName in ipairs(FDJ.ORDER) do
        local dung = FDJ.DB[dungeonName]
        if dung and dung.bosses then
            for bIdx, boss in ipairs(dung.bosses) do
                if boss.npcID then
                    FDJ.bossByNpcID[boss.npcID] = {
                        dungeon = dungeonName,
                        bossIndex = bIdx,
                        name = boss.name,
                    }
                end
                if boss.name then
                    FDJ.bossByName[boss.name:lower()] = {
                        dungeon = dungeonName,
                        bossIndex = bIdx,
                        name = boss.name,
                    }
                end
                if boss.aliases then
                    for _, alias in ipairs(boss.aliases) do
                        FDJ.bossByName[alias:lower()] = {
                            dungeon = dungeonName,
                            bossIndex = bIdx,
                            name = boss.name,
                        }
                    end
                end
            end
        end
    end
end

function FDJ.IsBossDefeated(dungeonName, bossIndex)
    if not dungeonName or not bossIndex then return false end
    local byDung = FDJ.defeatedBosses[dungeonName]
    return (byDung and byDung[bossIndex]) == true
end

function FDJ.SetBossDefeated(dungeonName, bossIndex, isDefeated)
    if not dungeonName or not bossIndex then return end
    FDJ.defeatedBosses[dungeonName] = FDJ.defeatedBosses[dungeonName] or {}
    FDJ.defeatedBosses[dungeonName][bossIndex] = isDefeated and true or nil
end

function FDJ.ResetDefeatedBosses(dungeonName)
    if dungeonName then
        FDJ.defeatedBosses[dungeonName] = nil
    else
        FDJ.defeatedBosses = {}
    end
end

-- ============================================================
-- LOOT WISHLIST & CHASE ITEM TRACKER (Per-Character DB)
-- ============================================================
function FDJ.GetCharKey()
    if UnitName then
        local name = UnitName("player")
        if name and name ~= "" then
            return Ambiguate and Ambiguate(name, "none") or name
        end
    end
    return "Default"
end

function FDJ.IsWishlisted(itemID)
    if not itemID then return false end
    itemID = tonumber(itemID)
    local charKey = FDJ.GetCharKey()
    ForeverDungeonJournalDB = ForeverDungeonJournalDB or {}
    ForeverDungeonJournalDB.wishlists = ForeverDungeonJournalDB.wishlists or {}
    local charWishlist = ForeverDungeonJournalDB.wishlists[charKey]
    return (charWishlist and charWishlist[itemID]) == true
end

function FDJ.ToggleWishlist(itemID)
    if not itemID then return false end
    itemID = tonumber(itemID)
    local charKey = FDJ.GetCharKey()
    ForeverDungeonJournalDB = ForeverDungeonJournalDB or {}
    ForeverDungeonJournalDB.wishlists = ForeverDungeonJournalDB.wishlists or {}
    ForeverDungeonJournalDB.wishlists[charKey] = ForeverDungeonJournalDB.wishlists[charKey] or {}
    local charWishlist = ForeverDungeonJournalDB.wishlists[charKey]
    if charWishlist[itemID] then
        charWishlist[itemID] = nil
        return false
    else
        charWishlist[itemID] = true
        return true
    end
end

function FDJ.GetWishlistItems()
    local charKey = FDJ.GetCharKey()
    ForeverDungeonJournalDB = ForeverDungeonJournalDB or {}
    ForeverDungeonJournalDB.wishlists = ForeverDungeonJournalDB.wishlists or {}
    local charWishlist = ForeverDungeonJournalDB.wishlists[charKey] or {}
    local results = {}
    if not FDJ.DB or not FDJ.ORDER then return results end

    for _, dungeonName in ipairs(FDJ.ORDER) do
        local dung = FDJ.DB[dungeonName]
        if dung and dung.bosses then
            for bIdx, boss in ipairs(dung.bosses) do
                if boss.loot then
                    for _, item in ipairs(boss.loot) do
                        local itemID = tonumber(item[1])
                        if itemID and charWishlist[itemID] then
                            local rawSlot = item[3]
                            local rawQuality = item[4]
                            if type(rawSlot) == "number" and type(rawQuality) == "string" then
                                rawSlot, rawQuality = rawQuality, rawSlot
                            end
                            results[#results + 1] = {
                                itemID = itemID,
                                name = item[2],
                                slot = rawSlot,
                                quality = rawQuality,
                                dungeon = dungeonName,
                                boss = boss.name,
                                bossIndex = bIdx,
                            }
                        end
                    end
                end
            end
        end
    end
    return results
end


-- ============================================================
-- One-time notice. Shown once after the first login/reload with this
-- version installed; pressing OK stores a flag in SavedVariables so it never
-- appears again. Bump NOTICE_ID to show a new message in a later update.
-- ============================================================
local NOTICE_ID = "lv30-data-v1"

local function ShowUpdateNotice(force)
    local db = ForeverDungeonJournalDB
    if type(db) ~= "table" then return end
    db.seenNotices = db.seenNotices or {}
    if db.seenNotices[NOTICE_ID] and not force then return end
    if _G.ForeverDungeonJournalNotice then
        _G.ForeverDungeonJournalNotice:Show()
        return
    end

    local L = FDJ.L or function(key) return key end

    local f = CreateFrame("Frame", "ForeverDungeonJournalNotice", UIParent, BackdropTemplateMixin and "BackdropTemplate" or nil)
    f:SetSize(380, 170)
    f:SetPoint("CENTER", UIParent, "CENTER", 0, 120)
    f:SetFrameStrata("DIALOG")
    f:SetToplevel(true)
    f:EnableMouse(true)
    f:SetMovable(true)
    f:RegisterForDrag("LeftButton")
    f:SetScript("OnDragStart", f.StartMoving)
    f:SetScript("OnDragStop", f.StopMovingOrSizing)
    if f.SetBackdrop then
        f:SetBackdrop({
            bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
            edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
            tile = true, tileSize = 32, edgeSize = 32,
            insets = { left = 11, right = 12, top = 12, bottom = 11 },
        })
    end

    -- Title row: "Dungeon Journal" with the journal's icon.
    local icon = f:CreateTexture(nil, "ARTWORK")
    icon:SetTexture("Interface\\Icons\\INV_Misc_Book_09")
    icon:SetSize(30, 30)
    icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)

    local title = f:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    title:SetText(L("DUNGEON_JOURNAL"))

    -- Centre icon + title together.
    local titleWidth = (title:GetStringWidth() or 150) + 30 + 8
    icon:SetPoint("TOPLEFT", f, "TOP", -titleWidth / 2, -22)
    title:SetPoint("LEFT", icon, "RIGHT", 8, 0)

    local body = f:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
    body:SetPoint("TOPLEFT", f, "TOPLEFT", 26, -64)
    body:SetPoint("TOPRIGHT", f, "TOPRIGHT", -26, -64)
    body:SetJustifyH("CENTER")
    body:SetJustifyV("TOP")
    if body.SetWordWrap then body:SetWordWrap(true) end
    body:SetText(L("NOTICE_LV30_DATA"))

    local ok = CreateFrame("Button", nil, f, "UIPanelButtonTemplate")
    ok:SetSize(110, 24)
    ok:SetPoint("BOTTOM", f, "BOTTOM", 0, 20)
    ok:SetText(OKAY or "OK")
    ok:SetScript("OnClick", function()
        db.seenNotices[NOTICE_ID] = true
        f:Hide()
    end)

    -- Grow the box if a translation needs more lines.
    local needed = 64 + (body:GetStringHeight() or 40) + 60
    if needed > f:GetHeight() then f:SetHeight(needed) end

    if PlaySound and SOUNDKIT and SOUNDKIT.IG_MAINMENU_OPEN then
        pcall(PlaySound, SOUNDKIT.IG_MAINMENU_OPEN)
    end
    f:Show()
end

FDJ.ShowUpdateNotice = ShowUpdateNotice

local noticeEvents = CreateFrame("Frame")
noticeEvents:RegisterEvent("PLAYER_ENTERING_WORLD")
noticeEvents:SetScript("OnEvent", function(self)
    self:UnregisterEvent("PLAYER_ENTERING_WORLD")
    -- Small delay so it appears after the loading screen and other addons.
    if C_Timer and C_Timer.After then
        C_Timer.After(3, ShowUpdateNotice)
    else
        ShowUpdateNotice()
    end
end)
