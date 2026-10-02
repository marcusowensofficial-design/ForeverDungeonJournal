import sys
import re

with open("Core/Journal.lua", "r", encoding="utf-8") as f:
    content = f.read()

print("Original length:", len(content))

# 1. Remove redundant FDJ.DUNGEON_MAPS
pattern_maps = r"FDJ\.DUNGEON_MAPS = \{.*?\}\n\nfunction FDJ\.LanguageDisplayName"
match_maps = re.search(pattern_maps, content, re.DOTALL)
if not match_maps:
    print("ERROR: Could not find FDJ.DUNGEON_MAPS block")
    sys.exit(1)

content = content[:match_maps.start()] + "-- Custom dungeon map pages are loaded from Data/DungeonMaps.lua (FDJ.DUNGEON_MAPS)\n\nfunction FDJ.LanguageDisplayName" + content[match_maps.end():]
print("Removed redundant FDJ.DUNGEON_MAPS successfully")

# 2. Update DUNGEON_SEARCH_ALIASES
target_alias = '        ["Blackfathom Deeps"] = { "bfd" },'
replacement_alias = '''        ["Blackfathom Deeps"] = { "bfd" },
        ["Excavation Site: Wetlands"] = { "wetlands", "excavation", "site", "esw" },
        ["City of Dalaran"] = { "dalaran", "dal", "sewers", "underbelly" },
        ["Gnomeregan"] = { "gnomer", "gnome", "thermaplugg" },
        ["Razorfen Kraul"] = { "rfk", "kraul", "razorfen" },
        ["Scarlet Monastery: Graveyard"] = { "sm gy", "gy", "graveyard", "monastery" },'''

if target_alias not in content:
    print("ERROR: Could not find target_alias")
    sys.exit(1)

content = content.replace(target_alias, replacement_alias, 1)
print("Updated DUNGEON_SEARCH_ALIASES successfully")

# 3. Add FDJ.BuildItemLookup and FDJ.InitTooltipHooks in PLAYER_LOGIN
target_login = '''        if FDJ.BuildBossLookups then
            FDJ.BuildBossLookups()
        end'''

replacement_login = '''        if FDJ.BuildBossLookups then
            FDJ.BuildBossLookups()
        end

        if FDJ.BuildItemLookup then
            FDJ.BuildItemLookup()
        end

        if FDJ.InitTooltipHooks then
            FDJ.InitTooltipHooks()
        end'''

if target_login not in content:
    print("ERROR: Could not find target_login")
    sys.exit(1)

content = content.replace(target_login, replacement_login, 1)
print("Updated PLAYER_LOGIN successfully")

# 4. Hide homeLootExplorerPanel in ShowDungeonPage and ShowHomePage
target_show_dungeon = '''ShowDungeonPage = function()
    if not frame then return end
    if frame.homeWishlistPanel then frame.homeWishlistPanel:Hide() end'''

replacement_show_dungeon = '''ShowDungeonPage = function()
    if not frame then return end
    if frame.homeWishlistPanel then frame.homeWishlistPanel:Hide() end
    if frame.homeLootExplorerPanel then frame.homeLootExplorerPanel:Hide() end'''

if target_show_dungeon not in content:
    print("ERROR: Could not find target_show_dungeon")
    sys.exit(1)

content = content.replace(target_show_dungeon, replacement_show_dungeon, 1)

target_show_home = '''ShowHomePage = function()
    if not frame then return end
    if frame.contentPanel then frame.contentPanel:Hide() end
    if frame.homeWishlistPanel then frame.homeWishlistPanel:Hide() end'''

replacement_show_home = '''ShowHomePage = function()
    if not frame then return end
    if frame.contentPanel then frame.contentPanel:Hide() end
    if frame.homeWishlistPanel then frame.homeWishlistPanel:Hide() end
    if frame.homeLootExplorerPanel then frame.homeLootExplorerPanel:Hide() end'''

if target_show_home not in content:
    print("ERROR: Could not find target_show_home")
    sys.exit(1)

content = content.replace(target_show_home, replacement_show_home, 1)
print("Updated ShowDungeonPage and ShowHomePage successfully")

# 5. Update GET_ITEM_INFO_RECEIVED to refresh homeLootExplorerPanel if shown
target_item_event = '''            if frame.homeWishlistPanel and frame.homeWishlistPanel:IsShown() and FDJ.RefreshWishlistPanel then
                FDJ.RefreshWishlistPanel()
            end'''

replacement_item_event = '''            if frame.homeWishlistPanel and frame.homeWishlistPanel:IsShown() and FDJ.RefreshWishlistPanel then
                FDJ.RefreshWishlistPanel()
            end
            if frame.homeLootExplorerPanel and frame.homeLootExplorerPanel:IsShown() and FDJ.RefreshLootExplorerPanel then
                FDJ.RefreshLootExplorerPanel()
            end'''

if target_item_event not in content:
    print("ERROR: Could not find target_item_event")
    sys.exit(1)

content = content.replace(target_item_event, replacement_item_event, 1)
print("Updated GET_ITEM_INFO_RECEIVED successfully")

# 6. Add homeLootExplorerButton and homeLootExplorerPanel
# We hook right around homeWishlistButton and homeWishlistPanel
target_wishlist_btn = '''    local homeWishlistButton = CreateFrame("Button", nil, home, "BackdropTemplate")
    frame.homeWishlistButton = homeWishlistButton
    homeWishlistButton:SetSize(136, 28)
    homeWishlistButton:SetPoint("RIGHT", hideDungeonsButton, "LEFT", -10, 0)'''

replacement_wishlist_btn = '''    local homeLootExplorerButton = CreateFrame("Button", nil, home, "BackdropTemplate")
    frame.homeLootExplorerButton = homeLootExplorerButton
    homeLootExplorerButton:SetSize(132, 28)
    homeLootExplorerButton:SetPoint("RIGHT", hideDungeonsButton, "LEFT", -10, 0)
    FDJ.SetBackdrop(homeLootExplorerButton, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\Tooltips\\\\UI-Tooltip-Border", 12, 4)
    homeLootExplorerButton:SetBackdropColor(0.12, 0.09, 0.05, 0.95)
    homeLootExplorerButton:SetBackdropBorderColor(0.65, 0.48, 0.22, 1)
    homeLootExplorerButton:SetHighlightTexture("Interface\\\\QuestFrame\\\\UI-QuestTitleHighlight", "ADD")
    local homeLootExplorerButtonText = homeLootExplorerButton:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    homeLootExplorerButtonText:SetPoint("CENTER", 0, 0)
    homeLootExplorerButtonText:SetTextColor(1.0, 0.82, 0.25)
    local lootExpLabel = L("LOOT_EXPLORER")
    if not lootExpLabel or lootExpLabel == "LOOT_EXPLORER" then lootExpLabel = "Loot Explorer" end
    homeLootExplorerButtonText:SetText("|TInterface\\\\Icons\\\\INV_Misc_Bag_08:14:14:0:0:64:64:4:60:4:60|t " .. lootExpLabel)
    frame.homeLootExplorerButtonText = homeLootExplorerButtonText

    local homeWishlistButton = CreateFrame("Button", nil, home, "BackdropTemplate")
    frame.homeWishlistButton = homeWishlistButton
    homeWishlistButton:SetSize(136, 28)
    homeWishlistButton:SetPoint("RIGHT", homeLootExplorerButton, "LEFT", -10, 0)'''

if target_wishlist_btn not in content:
    print("ERROR: Could not find target_wishlist_btn")
    sys.exit(1)

content = content.replace(target_wishlist_btn, replacement_wishlist_btn, 1)

# Now add click/hover scripts and the Loot Explorer panel implementation right after the wishlist panel!
target_after_wpanel = '''    local wEmpty = wPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    frame.homeWishlistEmptyText = wEmpty
    wEmpty:SetPoint("CENTER", wPanel, "CENTER", 0, -20)
    wEmpty:SetWidth(450)
    wEmpty:SetJustifyH("CENTER")
    wEmpty:SetText(L("NO_WISHLIST_ITEMS"))
    wEmpty:SetTextColor(0.65, 0.60, 0.50)
    wEmpty:Hide()'''

loot_explorer_impl = '''    local wEmpty = wPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    frame.homeWishlistEmptyText = wEmpty
    wEmpty:SetPoint("CENTER", wPanel, "CENTER", 0, -20)
    wEmpty:SetWidth(450)
    wEmpty:SetJustifyH("CENTER")
    wEmpty:SetText(L("NO_WISHLIST_ITEMS"))
    wEmpty:SetTextColor(0.65, 0.60, 0.50)
    wEmpty:Hide()

    -- ============================================================
    -- HOME LOOT EXPLORER PANEL
    -- ============================================================
    local lePanel = CreateFrame("Frame", nil, home, "BackdropTemplate")
    frame.homeLootExplorerPanel = lePanel
    lePanel:SetSize(720, 500)
    lePanel:SetPoint("CENTER", home, "CENTER", 0, -10)
    lePanel:SetFrameLevel(home:GetFrameLevel() + 50)
    FDJ.SetBackdrop(lePanel, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\DialogFrame\\\\UI-DialogBox-Border", 20, 4)
    lePanel:SetBackdropColor(0.08, 0.06, 0.04, 0.98)
    lePanel:SetBackdropBorderColor(0.65, 0.48, 0.22, 1)
    lePanel:Hide()

    local leTitle = lePanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    leTitle:SetPoint("TOPLEFT", 22, -14)
    leTitle:SetText("|TInterface\\\\Icons\\\\INV_Misc_Bag_08:18:18:0:0:64:64:4:60:4:60|t  " .. lootExpLabel)
    leTitle:SetTextColor(1.0, 0.82, 0.25)

    local leSub = lePanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    leSub:SetPoint("TOPLEFT", leTitle, "BOTTOMLEFT", 0, -2)
    leSub:SetText("Filter and browse dungeon loot. Click an item to view its boss encounter.")
    leSub:SetTextColor(0.70, 0.65, 0.55)

    local leClose = CreateFrame("Button", nil, lePanel, "UIPanelCloseButton")
    leClose:SetPoint("TOPRIGHT", -4, -4)
    leClose:SetScript("OnClick", function() lePanel:Hide() end)

    homeLootExplorerButton:SetScript("OnClick", function()
        FDJ.PlayJournalOptionSound()
        if lePanel:IsShown() then
            lePanel:Hide()
        else
            if frame.homeWishlistPanel then frame.homeWishlistPanel:Hide() end
            FDJ.RefreshLootExplorerPanel()
            lePanel:Show()
        end
    end)
    homeLootExplorerButton:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(lootExpLabel, 1, 0.82, 0)
        GameTooltip:AddLine("Browse and search items from all dungeons by slot or level bracket.", 0.9, 0.9, 0.9, true)
        GameTooltip:Show()
    end)
    homeLootExplorerButton:SetScript("OnLeave", function() GameTooltip:Hide() end)

    -- Filter States
    local leSelectedSlot = "ALL"
    local leSelectedBracket = "ALL"
    local leSearchQuery = ""

    local slotButtons = {}
    local bracketButtons = {}

    local function StyleFilterChip(btn, isSelected)
        if isSelected then
            btn:SetBackdropColor(0.38, 0.26, 0.10, 1.0)
            btn:SetBackdropBorderColor(1.00, 0.82, 0.25, 1.0)
            if btn.text then btn.text:SetTextColor(1.00, 0.90, 0.40) end
        else
            btn:SetBackdropColor(0.14, 0.10, 0.06, 0.85)
            btn:SetBackdropBorderColor(0.40, 0.30, 0.15, 0.9)
            if btn.text then btn.text:SetTextColor(0.70, 0.65, 0.55) end
        end
    end

    -- Filter Bar: Slots
    local slotFilterBar = CreateFrame("Frame", nil, lePanel)
    slotFilterBar:SetSize(670, 24)
    slotFilterBar:SetPoint("TOPLEFT", 22, -50)

    local slotDefs = {
        { id = "ALL", label = "All Slots" },
        { id = "WEAPONS", label = "Weapons" },
        { id = "CLOTH", label = "Cloth" },
        { id = "LEATHER", label = "Leather" },
        { id = "MAIL", label = "Mail" },
        { id = "ACCESSORIES", label = "Accessories" },
    }

    local prevSlotBtn = nil
    for _, def in ipairs(slotDefs) do
        local btn = CreateFrame("Button", nil, slotFilterBar, "BackdropTemplate")
        btn:SetHeight(22)
        FDJ.SetBackdrop(btn, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\Tooltips\\\\UI-Tooltip-Border", 10, 2)
        btn:SetHighlightTexture("Interface\\\\QuestFrame\\\\UI-QuestTitleHighlight", "ADD")

        local txt = btn:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        txt:SetPoint("CENTER", 0, 0)
        txt:SetText(def.label)
        btn.text = txt

        local w = math.max(50, math.ceil((txt:GetStringWidth() or 40) + 16))
        btn:SetWidth(w)

        if not prevSlotBtn then
            btn:SetPoint("LEFT", slotFilterBar, "LEFT", 0, 0)
        else
            btn:SetPoint("LEFT", prevSlotBtn, "RIGHT", 6, 0)
        end
        prevSlotBtn = btn

        btn:SetScript("OnClick", function()
            FDJ.PlayJournalOptionSound()
            leSelectedSlot = def.id
            for _, b in ipairs(slotButtons) do
                StyleFilterChip(b, b.filterId == leSelectedSlot)
            end
            FDJ.RefreshLootExplorerPanel()
        end)
        btn.filterId = def.id
        slotButtons[#slotButtons + 1] = btn
        StyleFilterChip(btn, def.id == "ALL")
    end

    -- Filter Bar: Level Brackets & Search Box
    local bracketFilterBar = CreateFrame("Frame", nil, lePanel)
    bracketFilterBar:SetSize(670, 24)
    bracketFilterBar:SetPoint("TOPLEFT", 22, -78)

    local bracketDefs = {
        { id = "ALL", label = "All Lvls" },
        { id = "13-20", label = "13–20" },
        { id = "20-28", label = "20–28" },
        { id = "28-38", label = "28–38" },
    }

    local prevBktBtn = nil
    for _, def in ipairs(bracketDefs) do
        local btn = CreateFrame("Button", nil, bracketFilterBar, "BackdropTemplate")
        btn:SetHeight(22)
        FDJ.SetBackdrop(btn, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\Tooltips\\\\UI-Tooltip-Border", 10, 2)
        btn:SetHighlightTexture("Interface\\\\QuestFrame\\\\UI-QuestTitleHighlight", "ADD")

        local txt = btn:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        txt:SetPoint("CENTER", 0, 0)
        txt:SetText(def.label)
        btn.text = txt

        local w = math.max(45, math.ceil((txt:GetStringWidth() or 35) + 14))
        btn:SetWidth(w)

        if not prevBktBtn then
            btn:SetPoint("LEFT", bracketFilterBar, "LEFT", 0, 0)
        else
            btn:SetPoint("LEFT", prevBktBtn, "RIGHT", 6, 0)
        end
        prevBktBtn = btn

        btn:SetScript("OnClick", function()
            FDJ.PlayJournalOptionSound()
            leSelectedBracket = def.id
            for _, b in ipairs(bracketButtons) do
                StyleFilterChip(b, b.filterId == leSelectedBracket)
            end
            FDJ.RefreshLootExplorerPanel()
        end)
        btn.filterId = def.id
        bracketButtons[#bracketButtons + 1] = btn
        StyleFilterChip(btn, def.id == "ALL")
    end

    -- Search Box
    local leSearchBox = CreateFrame("EditBox", nil, bracketFilterBar, "BackdropTemplate")
    leSearchBox:SetSize(170, 22)
    leSearchBox:SetPoint("RIGHT", bracketFilterBar, "RIGHT", 0, 0)
    FDJ.SetBackdrop(leSearchBox, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\Tooltips\\\\UI-Tooltip-Border", 10, 2)
    leSearchBox:SetBackdropColor(0.06, 0.05, 0.04, 0.95)
    leSearchBox:SetBackdropBorderColor(0.40, 0.30, 0.15, 0.9)
    leSearchBox:SetFontObject("GameFontHighlightSmall")
    leSearchBox:SetTextInsets(6, 6, 0, 0)
    leSearchBox:SetAutoFocus(false)

    local leSearchPlaceholder = leSearchBox:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    leSearchPlaceholder:SetPoint("LEFT", 6, 0)
    leSearchPlaceholder:SetText("Search loot or boss...")

    leSearchBox:SetScript("OnTextChanged", function(self)
        local val = self:GetText()
        if leSearchPlaceholder then
            leSearchPlaceholder:SetShown(not val or val == "")
        end
        leSearchQuery = val or ""
        FDJ.RefreshLootExplorerPanel()
    end)
    leSearchBox:SetScript("OnEscapePressed", function(self)
        self:SetText("")
        self:ClearFocus()
    end)

    -- Column Headers Bar
    local leHeaderBar = CreateFrame("Frame", nil, lePanel)
    leHeaderBar:SetSize(660, 18)
    leHeaderBar:SetPoint("TOPLEFT", 26, -106)

    local leHItem = leHeaderBar:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    leHItem:SetPoint("LEFT", 0, 0)
    leHItem:SetText("ITEM & STATS")
    leHItem:SetTextColor(0.70, 0.60, 0.40)

    local leHSlot = leHeaderBar:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    leHSlot:SetPoint("LEFT", 280, 0)
    leHSlot:SetText("SLOT & REQUIREMENTS")
    leHSlot:SetTextColor(0.70, 0.60, 0.40)

    local leHSource = leHeaderBar:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    leHSource:SetPoint("RIGHT", -44, 0)
    leHSource:SetText("ENCOUNTER SOURCE")
    leHSource:SetTextColor(0.70, 0.60, 0.40)

    -- Scroll Frame
    local leScroll = CreateFrame("ScrollFrame", "ForeverDungeonJournalLootExplorerScroll", lePanel, "UIPanelScrollFrameTemplate")
    frame.homeLootExplorerScroll = leScroll
    leScroll:SetPoint("TOPLEFT", 18, -126)
    leScroll:SetPoint("BOTTOMRIGHT", -34, 16)

    local leContent = CreateFrame("Frame", nil, leScroll)
    leContent:SetSize(660, 1)
    leScroll:SetScrollChild(leContent)
    frame.homeLootExplorerContent = leContent

    local leEmpty = lePanel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    frame.homeLootExplorerEmptyText = leEmpty
    leEmpty:SetPoint("CENTER", lePanel, "CENTER", 0, -20)
    leEmpty:SetWidth(450)
    leEmpty:SetJustifyH("CENTER")
    leEmpty:SetText("No dungeon items match the selected filters.")
    leEmpty:SetTextColor(0.65, 0.60, 0.50)
    leEmpty:Hide()

    -- Filter Query Helper
    function FDJ.GetFilteredLootExplorerItems(slotFilter, bracketFilter, query)
        local results = {}
        if not FDJ.DB or not FDJ.ORDER then return results end
        query = (query and query:gsub("^%s*(.-)%s*$", "%1") ~= "") and string.lower(query:gsub("^%s*(.-)%s*$", "%1")) or nil

        for _, dungeonName in ipairs(FDJ.ORDER) do
            local dung = FDJ.DB[dungeonName]
            if dung and dung.bosses then
                local matchBracket = true
                if bracketFilter and bracketFilter ~= "ALL" then
                    local minLvl, maxLvl = 0, 0
                    if dung.level then
                        local s1, s2 = dung.level:match("(%d+)%-(%d+)")
                        minLvl = tonumber(s1) or 0
                        maxLvl = tonumber(s2) or 0
                    end
                    if bracketFilter == "13-20" then
                        matchBracket = (minLvl <= 20 and maxLvl <= 26)
                    elseif bracketFilter == "20-28" then
                        matchBracket = (minLvl >= 20 and minLvl < 28)
                    elseif bracketFilter == "28-38" then
                        matchBracket = (minLvl >= 28)
                    end
                end

                if matchBracket then
                    for bIdx, boss in ipairs(dung.bosses) do
                        if boss.loot then
                            for _, item in ipairs(boss.loot) do
                                local itemID = tonumber(item[1])
                                local itemName = item[2]
                                local rawSlot = item[3]
                                local rawQuality = item[4]
                                if type(rawSlot) == "number" and type(rawQuality) == "string" then
                                    rawSlot, rawQuality = rawQuality, rawSlot
                                end

                                local matchSlot = true
                                if slotFilter and slotFilter ~= "ALL" then
                                    local sLower = string.lower(tostring(rawSlot or ""))
                                    if slotFilter == "WEAPONS" then
                                        matchSlot = sLower:find("weapon") or sLower:find("one%-hand") or sLower:find("two%-hand")
                                            or sLower:find("main hand") or sLower:find("off hand") or sLower:find("dagger")
                                            or sLower:find("sword") or sLower:find("axe") or sLower:find("mace")
                                            or sLower:find("staff") or sLower:find("polearm") or sLower:find("bow")
                                            or sLower:find("gun") or sLower:find("crossbow") or sLower:find("wand")
                                            or sLower:find("shield") or sLower:find("held in off%-hand")
                                    elseif slotFilter == "CLOTH" then
                                        matchSlot = sLower:find("cloth")
                                    elseif slotFilter == "LEATHER" then
                                        matchSlot = sLower:find("leather")
                                    elseif slotFilter == "MAIL" then
                                        matchSlot = sLower:find("mail")
                                    elseif slotFilter == "ACCESSORIES" then
                                        matchSlot = sLower:find("neck") or sLower:find("finger") or sLower:find("ring")
                                            or sLower:find("trinket") or sLower:find("back") or sLower:find("cloak")
                                    end
                                end

                                local matchQuery = true
                                if query then
                                    local nameLower = string.lower(tostring(itemName or ""))
                                    local bossLower = string.lower(tostring(boss.name or ""))
                                    local dungLower = string.lower(tostring(dungeonName or ""))
                                    matchQuery = nameLower:find(query, 1, true) or bossLower:find(query, 1, true) or dungLower:find(query, 1, true)
                                end

                                if matchSlot and matchQuery then
                                    results[#results + 1] = {
                                        itemID = itemID,
                                        name = itemName,
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
        end
        return results
    end

    FDJ.RefreshLootExplorerPanel = function()
        if not frame.homeLootExplorerPanel or not frame.homeLootExplorerContent then return end
        local items = FDJ.GetFilteredLootExplorerItems(leSelectedSlot, leSelectedBracket, leSearchQuery)
        local rows = frame.lootExplorerRows or {}
        frame.lootExplorerRows = rows

        for i = 1, math.max(#rows, #items) do
            local row = rows[i]
            if i <= #items then
                if not row then
                    row = CreateFrame("Button", nil, frame.homeLootExplorerContent, "BackdropTemplate")
                    row:SetSize(660, 50)
                    FDJ.SetBackdrop(row, "Interface\\\\Buttons\\\\WHITE8X8", "Interface\\\\Tooltips\\\\UI-Tooltip-Border", 10, 2)
                    row:SetBackdropColor(0.16, 0.12, 0.07, 0.92)
                    row:SetBackdropBorderColor(0.42, 0.30, 0.15, 1)
                    row:SetHighlightTexture("Interface\\\\QuestFrame\\\\UI-QuestTitleHighlight", "ADD")

                    row.icon = row:CreateTexture(nil, "ARTWORK")
                    row.icon:SetSize(36, 36)
                    row.icon:SetPoint("LEFT", 7, 0)
                    row.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)

                    row.iconBorder = row:CreateTexture(nil, "OVERLAY")
                    row.iconBorder:SetSize(40, 40)
                    row.iconBorder:SetPoint("CENTER", row.icon, "CENTER", 0, 0)
                    row.iconBorder:SetTexture("Interface\\\\Common\\\\WhiteIconFrame")

                    row.name = row:CreateFontString(nil, "OVERLAY", "GameFontNormal")
                    row.name:SetPoint("TOPLEFT", row.icon, "TOPRIGHT", 10, -6)
                    row.name:SetWidth(235)
                    row.name:SetJustifyH("LEFT")
                    row.name:SetWordWrap(false)

                    row.stats = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
                    row.stats:SetPoint("BOTTOMLEFT", row.icon, "BOTTOMRIGHT", 10, 6)
                    row.stats:SetWidth(240)
                    row.stats:SetJustifyH("LEFT")
                    row.stats:SetWordWrap(false)

                    row.slotType = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
                    row.slotType:SetPoint("TOPLEFT", row.icon, "TOPRIGHT", 255, -6)
                    row.slotType:SetWidth(140)
                    row.slotType:SetJustifyH("LEFT")
                    row.slotType:SetWordWrap(false)

                    row.reqLevel = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
                    row.reqLevel:SetPoint("BOTTOMLEFT", row.icon, "BOTTOMRIGHT", 255, 6)
                    row.reqLevel:SetWidth(140)
                    row.reqLevel:SetJustifyH("LEFT")
                    row.reqLevel:SetWordWrap(false)

                    row.dungeon = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
                    row.dungeon:SetPoint("TOPRIGHT", -36, -6)
                    row.dungeon:SetWidth(160)
                    row.dungeon:SetJustifyH("RIGHT")
                    row.dungeon:SetWordWrap(false)

                    row.boss = row:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
                    row.boss:SetPoint("BOTTOMRIGHT", -36, 6)
                    row.boss:SetWidth(160)
                    row.boss:SetJustifyH("RIGHT")
                    row.boss:SetWordWrap(false)

                    row.starBtn = CreateFrame("Button", nil, row)
                    row.starBtn:SetSize(22, 22)
                    row.starBtn:SetPoint("RIGHT", -8, 0)
                    row.starBtn.icon = row.starBtn:CreateTexture(nil, "ARTWORK")
                    row.starBtn.icon:SetAllPoints()
                    row.starBtn.icon:SetTexture("Interface\\\\AddOns\\\\ForeverDungeonJournal\\\\Media\\\\Star_Gold.tga")
                    row.starBtn:SetHighlightTexture("Interface\\\\AddOns\\\\ForeverDungeonJournal\\\\Media\\\\Star_Gold.tga", "ADD")
                    local starHl = row.starBtn:GetHighlightTexture()
                    if starHl then
                        starHl:SetVertexColor(1.0, 0.95, 0.40, 0.50)
                    end

                    row.starBtn:SetScript("OnClick", function(self)
                        local parentR = self:GetParent()
                        if parentR and parentR.itemData then
                            local added = FDJ.ToggleWishlist(parentR.itemData.itemID)
                            if added then
                                self.icon:SetVertexColor(1.0, 0.82, 0.0, 1.0)
                                self.icon:SetAlpha(1.0)
                            else
                                self.icon:SetVertexColor(0.5, 0.45, 0.35, 0.4)
                                self.icon:SetAlpha(0.4)
                            end
                            if FDJ.RefreshWishlistPanel then FDJ.RefreshWishlistPanel() end
                            if FDJ.UpdateHomeWishlistButton then FDJ.UpdateHomeWishlistButton() end
                            if selectedMode == "bosses" and FDJ.RefreshLoot then FDJ.RefreshLoot() end
                        end
                    end)
                    row.starBtn:SetScript("OnEnter", function(self)
                        local parentR = self:GetParent()
                        local isWish = parentR and parentR.itemData and FDJ.IsWishlisted and FDJ.IsWishlisted(parentR.itemData.itemID)
                        self.icon:SetVertexColor(1.0, 0.95, 0.40, 1.0)
                        self.icon:SetAlpha(1.0)
                        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
                        if isWish then
                            GameTooltip:SetText(L("REMOVE_FROM_WISHLIST") or "Remove from Wishlist", 1, 0.85, 0.35)
                        else
                            GameTooltip:SetText(L("ADD_TO_WISHLIST") or "Add to Wishlist", 1, 0.85, 0.35)
                        end
                        GameTooltip:AddLine(L("WISHLIST_TOOLTIP_DESC") or "Track this item and receive in-game alerts when it drops.", 0.9, 0.9, 0.9, true)
                        GameTooltip:Show()
                    end)
                    row.starBtn:SetScript("OnLeave", function(self)
                        local parentR = self:GetParent()
                        local isWish = parentR and parentR.itemData and FDJ.IsWishlisted and FDJ.IsWishlisted(parentR.itemData.itemID)
                        if isWish then
                            self.icon:SetVertexColor(1.0, 0.82, 0.0, 1.0)
                            self.icon:SetAlpha(1.0)
                        else
                            self.icon:SetVertexColor(0.5, 0.45, 0.35, 0.4)
                            self.icon:SetAlpha(0.4)
                        end
                        GameTooltip:Hide()
                    end)

                    row:SetScript("OnEnter", function(self)
                        self:SetBackdropColor(0.24, 0.17, 0.09, 0.98)
                        self:SetBackdropBorderColor(0.85, 0.68, 0.28, 1.0)
                        if self.itemData and self.itemData.itemID then
                            local _, liveLink = FDJ.ItemInfo(self.itemData.itemID)
                            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
                            GameTooltip:SetHyperlink(liveLink or ("item:" .. tostring(self.itemData.itemID)))
                            GameTooltip:Show()
                        end
                    end)
                    row:SetScript("OnLeave", function(self)
                        self:SetBackdropColor(0.16, 0.12, 0.07, 0.92)
                        self:SetBackdropBorderColor(0.42, 0.30, 0.15, 1)
                        GameTooltip:Hide()
                    end)

                    row:SetScript("OnClick", function(self)
                        if not self.itemData then return end
                        local itemID = self.itemData.itemID
                        local _, link = FDJ.ItemInfo(itemID)
                        link = link or ("item:" .. tostring(itemID))

                        if link and IsModifiedClick and IsModifiedClick("CHATLINK") and ChatEdit_InsertLink then
                            local used = ChatEdit_InsertLink(link)
                            if used then return end
                        end

                        if link and IsModifiedClick and IsModifiedClick("DRESSUP") and DressUpItemLink then
                            DressUpItemLink(link)
                            return
                        end

                        lePanel:Hide()
                        FDJ.SelectDungeon(self.itemData.dungeon)
                        FDJ.SetMode("bosses")
                        FDJ.SelectBoss(self.itemData.bossIndex)
                        FDJ.SetBossSubTab("loot")
                    end)

                    if i == 1 then
                        row:SetPoint("TOPLEFT", frame.homeLootExplorerContent, "TOPLEFT", 0, 0)
                    else
                        row:SetPoint("TOPLEFT", rows[i - 1], "BOTTOMLEFT", 0, -5)
                    end
                    rows[i] = row
                end

                local it = items[i]
                row.itemData = it
                local liveName, liveLink, quality, _, reqLevel, classType, subType, _, equipLoc, texture = FDJ.ItemInfo(it.itemID)
                quality = quality or it.quality or 1

                local qc = ITEM_QUALITY_COLORS[quality] or { r = 1, g = 1, b = 1 }
                row.icon:SetTexture(texture or "Interface\\\\Icons\\\\INV_Misc_QuestionMark")
                row.iconBorder:SetVertexColor(qc.r, qc.g, qc.b)

                local displayName = liveName or it.name or ("Item #" .. it.itemID)
                row.name:SetText(displayName)
                row.name:SetTextColor(qc.r, qc.g, qc.b)

                local statsSummary = FDJ.GetItemStatsSummary(it.itemID)
                if statsSummary and statsSummary ~= "" then
                    row.stats:SetText(statsSummary)
                    row.stats:SetTextColor(0.82, 0.82, 0.82)
                else
                    row.stats:SetText(classType or "")
                    row.stats:SetTextColor(0.60, 0.60, 0.60)
                end

                local slotText = it.slot or ""
                if slotText == "" and equipLoc and equipLoc ~= "" then
                    slotText = _G[equipLoc] or equipLoc
                end
                row.slotType:SetText(slotText)
                row.slotType:SetTextColor(0.85, 0.75, 0.55)

                if reqLevel and reqLevel > 0 then
                    row.reqLevel:SetText(string.format("Req Level %d", reqLevel))
                    row.reqLevel:SetTextColor(0.65, 0.65, 0.65)
                else
                    row.reqLevel:SetText("")
                end

                row.dungeon:SetText(it.dungeon or "")
                row.dungeon:SetTextColor(1.00, 0.82, 0.25)
                row.boss:SetText(it.boss or "")
                row.boss:SetTextColor(0.70, 0.65, 0.55)

                local isWish = FDJ.IsWishlisted and FDJ.IsWishlisted(it.itemID)
                if isWish then
                    row.starBtn.icon:SetVertexColor(1.0, 0.82, 0.0, 1.0)
                    row.starBtn.icon:SetAlpha(1.0)
                else
                    row.starBtn.icon:SetVertexColor(0.5, 0.45, 0.35, 0.4)
                    row.starBtn.icon:SetAlpha(0.4)
                end

                row:Show()
            else
                if row then row:Hide() end
            end
        end

        local count = #items
        local contentH = math.max(1, count * 55)
        frame.homeLootExplorerContent:SetHeight(contentH)
        frame.homeLootExplorerEmptyText:SetShown(count == 0)
        FDJ.UpdateScrollBarVisibility(frame.homeLootExplorerScroll, contentH)
    end
'''

if target_after_wpanel not in content:
    print("ERROR: Could not find target_after_wpanel")
    sys.exit(1)

content = content.replace(target_after_wpanel, loot_explorer_impl, 1)
print("Added homeLootExplorerPanel implementation successfully")

with open("Core/Journal.lua", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Core/Journal.lua successfully. New length:", len(content))
