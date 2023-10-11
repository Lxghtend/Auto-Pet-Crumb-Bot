import subprocess
import asyncio
import wizwalker
import copy
import re
from time import time
from wizwalker.constants import Keycode
from wizwalker.memory import Window
from wizwalker import Client, client
from wizwalker.memory.memory_objects.window import Window
from wizwalker import ClientHandler
import pyautogui

#paths for clicking and checking
crownShopButton = ["WorldView", "windowHUD", "CrownShopButtonsWindow"]
spellBookClose = ["WorldView", "DeckConfiguration", "Close_Button"] #wont work for some reason?
feedToPet = ["WorldView", "DeckConfiguration", "FurnitureSpellbookPage", "windowForBtns", "Layout", "btnFeedPet"]
spellBookDecorationIcon = ["WorldView", "DeckConfiguration", "FurnitureSpellbookPage", "Tab_Decoration"]
petLevelUpClose = ["WorldView", "", "PetLevelUpWindow", "wndPetLevelBkg", "btnPetLevelClose"]
charStats = ["WorldView", "DeckConfiguration", "CharStats"]
crownsInvoiceClose = ["WorldView", "CrownShopDelInvoiceModalWindow", "CrownShopDelInvoice", "closeDeliveryInvoiceWindow"]
'''
treasureCardButton = 
deathSchoolButton =
sellAllButton = 
'''
quitButton = ['WorldView', 'DeckConfiguration', 'SettingPage', 'QuitButton']
logOutConfirm = ['MessageBoxModalWindow', 'messageBoxBG', 'messageBoxLayout', 'AdjustmentWindow', 'Layout', 'centerButton']
txtLocation  = ['WorldView', 'mainWindow', 'sprSubBanner', 'txtLocation']
playButton = ['WorldView', 'mainWindow', 'btnPlay']
petHasImprovedClose = ["WorldView", "DeckConfiguration", "FurnitureSpellbookPage", "PetGameRewards", "btnBack"]
confirmFeedToPet = ["WorldView", "DeckConfiguration", "MessageBoxModalWindow", "messageBoxBG", "messageBoxLayout", "AdjustmentWindow", "Layout", "leftButton"]

async def is_visible_by_path(base_window:Window, path: list[str]):
    # Credit to SirOlaf for the original function; I'm modifying it - credit ultimate314
    if window := await window_from_path(base_window, path):
        return await window.is_visible()
    return False

# Returns a window, given a path 
async def window_from_path(base_window:Window, path:list[str]) -> Window:
    # Credit to SirOlaf for the original function; I'm modifying it - credit ultimate314;  and now me i have stolen this mwah haha - milwr i think?
    if not path:
        return base_window
    for child in await base_window.children():
        if await child.name() == path[0]:
            if found_window := await window_from_path(child, path[1:]):
                return found_window
    return False


async def click_window_from_path(mouse_handler, base_window, path): #credit ultimate314
    try:
        await mouse_handler.click_window(await window_from_path(base_window, path))
    except:
        pass

async def click_window_until_gone(client, path): #i did this im very cool - milwr (ithink)
    while (window := await window_from_path(client.root_window, path)) and await is_visible_by_path(client.root_window, path):
            await client.mouse_handler.click_window(window)
            await asyncio.sleep(0.1)

async def readBackPackSpace(client: Client) -> str: # BIG FAT SHOUTOUT TO FAJ FOR THIS ONE, starr fixed it
    backPackSpace = ["WorldView", "DeckConfiguration", "FurnitureSpellbookPage", "inventorySpace"]
    if await is_visible_by_path(client.root_window, spellBookDecorationIcon):
         await click_window_from_path(client.mouse_handler, client.root_window, spellBookDecorationIcon)
    else:
        await client.send_key(Keycode.U)
        await click_window_from_path(client.mouse_handler, client.root_window, spellBookDecorationIcon)
    window : Window = await window_from_path(client.root_window, backPackSpace)
    if window:
      return await window.maybe_text()
    return ""

async def readPetLevelUp(client: Client) -> str: # FAJ MADE THIS ONE TOO, starr fixed it
    petLevelUpText = ["WorldView", "", "PetLevelUpWindow", "wndPetLevelBkg", "txtAnnounceText"]
    window : Window = await window_from_path(client.root_window, petLevelUpText)
    if window:
      return await window.maybe_text()
    return ""

async def readGoldAmount(client: Client) -> str: # just copied the other ones ig
    goldCharStat = ["WorldView", "DeckConfiguration", "", "ControlSprite", "Gold"]
    await client.send_key(Keycode.C)
    if await is_visible_by_path(client.root_window, goldCharStat):
        pass
    else: 
        await client.send_key(Keycode.C)
    window : Window = await window_from_path(client.root_window, goldCharStat)
    if window:
      return await window.maybe_text()
    return ""
    
async def checkBackPackSpace(client: Client):
    backPackSpace = await readBackPackSpace(client)
    backPackSpaceNeeded = backPackSpace #make a second one that is identical
    maxBackPackSpace = backPackSpace #a third
    maxBackPackSpace = backPackSpaceNeeded = re.findall("\d+", maxBackPackSpace)[1]
    backPackSpace = re.findall("\d+", backPackSpace)[0] #remove everything that isnt a number, and remove everything after the /
    backPackSpaceNeeded = re.findall("\d+", backPackSpaceNeeded)[1] #do the same thing except remove everything before the /
    backPackSpace = int(backPackSpace) #set at int
    backPackSpaceNeeded = int(backPackSpaceNeeded) #set as int
    maxBackPackSpace = int(maxBackPackSpace) #set as int, this was needed incase ppl havve increase bag space exilirs
    backPackSpaceNeeded = backPackSpaceNeeded - backPackSpace #little math
    backPackSpace = (backPackSpace - maxBackPackSpace)*-1 #backpackspace would be like 100, showing how many you had, so this would flip it to how much space you have left
    x = "Clear your bag! You need 49 space available. You have"
    y = backPackSpaceNeeded
    z = 'space availible.'
    if backPackSpace < 49:
        print(x,y,z)
        await client.close()
        input('Press Enter after you have cleared up space in your bag.')
        await setup()
        '''
        more unused code in case the user isnt looking
        print("Closing in 3.")
        await asyncio.sleep(1)
        print("Closing in 2.")
        await asyncio.sleep(1)
        print("Closing in 1.")
        await client.close()
        '''
    if backPackSpace >= 49:
        await client.send_key(Keycode.U)

async def detectPetLevelUp(client: Client): # faj basically redid this for me
    petLevelUpAnnoucement = await readPetLevelUp(client)
    petLevelUpAnnoucement = petLevelUpAnnoucement.split("HAS LEVELED UP TO ")[1]
    match petLevelUpAnnoucement:
        case "TEEN!":
            input("Pet has leveled up to Teen!  Press Enter to continue to Adult.")
            await click_window_from_path(client.mouse_handler, client.root_window, petLevelUpClose)
        case "ADULT!":
            input("Pet has leveled up to Adult!  Press Enter to continue to Ancient.")
            await click_window_from_path(client.mouse_handler, client.root_window, petLevelUpClose)
        case "ANCIENT!":
            input("Pet has leveled up to Ancient!  Press Enter to continue to Epic.")
            await click_window_from_path(client.mouse_handler, client.root_window, petLevelUpClose)
        case "EPIC!":
            input("Pet has leveled up to Epic!  Press Enter to continue to Mega.")
            await click_window_from_path(client.mouse_handler, client.root_window, petLevelUpClose)
        case "MEGA!":
            input("Pet has leveled up to Mega!  Press Enter to close.")
            await click_window_from_path(client.mouse_handler, client.root_window, petLevelUpClose)
            await client.close() # removes hooks and closes :O

async def feedPetCrumbs(client: Client):
    print('Feeding the crumbs to your pet...')
    if await is_visible_by_path(client.root_window, spellBookDecorationIcon):
        pass
    else: 
        await client.send_key(Keycode.U)
    await click_window_from_path(client.mouse_handler, client.root_window, spellBookDecorationIcon)
    if await is_visible_by_path(client.root_window, feedToPet):
        for i in range(49):
            await click_window_from_path(client.mouse_handler, client.root_window, feedToPet)
            await asyncio.sleep(0.1)
            await click_window_from_path(client.mouse_handler, client.root_window, confirmFeedToPet)
            await asyncio.sleep(0.1)
            while await is_visible_by_path(client.root_window, petHasImprovedClose):
                await asyncio.sleep(0.1)
                await click_window_from_path(client.mouse_handler, client.root_window, petHasImprovedClose)
            if await is_visible_by_path(client.root_window, petLevelUpClose):
                await asyncio.sleep(3)
                await detectPetLevelUp(client)
            await asyncio.sleep(0.5)
        await buyPetCrumbs(client)
    else: # if i got res to work id have to updt this
        await buyPetCrumbs(client)

async def checkGoldAmount(client: Client):
    goldCharStat = await readGoldAmount(client) #good luck reading this
    goldCharStat1 = goldCharStat # create another variable identical to the gold value
    goldCharStat = re.findall("\d+", goldCharStat)[0] #remove "<center>" from the value
    goldCharStat1 = re.findall("\d+", goldCharStat1)[1] #remove "/</center>" from the value
    goldCharStat2 = goldCharStat + goldCharStat1 # adds them up to get the full number
    goldCharStat2 = int(goldCharStat2) #this is all probably terrible code, but the value of goldcharstat before was <center>gold/</center>
    x = "You have"
    y = goldCharStat
    z = "gold!"
    if goldCharStat2 < 500:
        print(x,y,z)
        input('Press Enter after you have gold to start training.') #i should probably add a failsafe here?
        '''
        #kinda dont want this code in case they arent looking, also could add a restart?
        print("Closing in 3.")
        await asyncio.sleep(1)
        print("Closing in 2.")
        await asyncio.sleep(1)
        print("Closing in 1.")
        await asyncio.sleep(1)
        await client.close()
        '''
    else:
        await client.send_key(Keycode.C)

''' scrapped due to the fact i can just check zone name LOL!
async def checkIFBazaar(p, client: Client):
    await client.send_key(Keycode.ESC)
    await click_window_from_path(p.mouse_handler, p.root_window,  quitButton)
    await click_window_until_gone(p.mouse_handler, p.root_window,  logOutConfirm)
    while not is_visible_by_path(p.root_window, txtLocation):
        await asyncio.sleep(0.1)
    await window_from_path(p.root_window, txtLocation)
'''

''' might add a cfg file to turn this on but might as well just make it close and user does manually
async def sellEmpowers(p, client: Client):
    #check for bazaar rq
    if clientzone != bazaar
        await client.send_key(Keycode.P)
        await click_window_from_path(p.root_window, treasureCardButton)
        await click_window_from_path(p.root_window, deathSchoolButton)
        await click_window_from_path(p.root_window, sellAllButton) #might need to use xy :/ wtv
        await client.send_key(Keycode.ENTER)
    else: 
        await client.send_key(Keycode.HOME)

'''

'''
async def resChecker(client: Client):
    await client.send_key(Keycode.ESC)
    #read the window of res in settings
    if resolution = 1920x1080
        await buyPetCrumbs1920x1080()
    if resolution = 800x600
        await buyPetCrumbs800x600()
'''

'''
async def buyPetCrumbs800x600():
    await checkGoldAmount(client)
    await checkBackPackSpace(client)
    if await is_visible_by_path(client.root_window, spellBookDecorationIcon):
        await client.send_key(Keycode.U)
    if await is_visible_by_path(client.root_window, charStats):
        await client.send_key(Keycode.C)
    await click_window_from_path(client.mouse_handler, client.root_window,  crownShopButton)
    await asyncio.sleep(4)
    await client.mouse_handler.click() #clicks wishlist
    await client.mouse_handler.click() #clicks pack
    await client.mouse_handler.click() #clicks switch to gold
    await client.mouse_handler.click() #clicks the buy button
    await asyncio.sleep(0.2)
    for i in range(7): #repeat 7 times
        await client.mouse_handler.click() #clicks the up arrow
    await client.mouse_handler.click() #clicks the buy button
    for i in range(7): #repeat 7 times
        await asyncio.sleep(0.3)
        await client.mouse_handler.click() #clicks the continue button
    await client.mouse_handler.click() #clicks the close crown shop button
    await click_window_from_path(client.mouse_handler, client.root_window, crownsInvoiceClose) #closes invoice
    await client.send_key(Keycode.ENTER) #closes popup
    await feedPetCrumbs(client)
'''

async def buyPetCrumbs(client: Client):
    print('Checking gold...')
    await checkGoldAmount(client)
    print('Done!')
    print('Checking Backpack...')
    await checkBackPackSpace(client)
    print('Done!')
    print('Buying Pet Crumbs...')
    '''
    # this is the ideal way to do it but the root wont work for some reason, plz dm if u can fix this
    if await is_visible_by_path(client.root_window, spellBookClose):
        await click_window_until_gone(client.root_window, spellBookClose)
        await asyncio.sleep(0.1)
    '''
    if await is_visible_by_path(client.root_window, spellBookDecorationIcon):
        await client.send_key(Keycode.U)
    if await is_visible_by_path(client.root_window, charStats):
        await client.send_key(Keycode.C)
    await click_window_from_path(client.mouse_handler, client.root_window,  crownShopButton)
    await asyncio.sleep(4)
    #  scrapped cuz it DOESNT WORK but it is the most practical way :(, dm if u know how to use search bar
    '''
    await client.mouse_handler.click(1299, 115) #clicks the housing tab
    await client.mouse_handler.click(1359, 216) #clicks the search bar
    await client.send_key(Keycode.C)
    await client.send_key(Keycode.R)
    await client.send_key(Keycode.U)
    await client.send_key(Keycode.M)
    await client.send_key(Keycode.B)
    await client.mouse_handler.click(480, 525) #clicks the pack
    '''
    packs = pyautogui.locateCenterOnScreen("packs.png") #clicks pack tab
    await pyautogui.click(packs)
    await asyncio.sleep(1)
    search = pyautogui.locateCenterOnScreen("search.png") #clicks search bar
    await pyautogui.click(search)
    crumb = "crumb"
    await pyautogui.write(crumb) #searches for the pack
    asyncio.sleep(0.5)
    pack = pyautogui.locateCenterOnScreen("pack.png") #clicks pack
    await pyautigui.click(pack)
    await asyncio.sleep(1)
    gold = pyautogui.locateCenterOnScreen("gold.png") #clicks switch to gold
    await pyautogui.click(gold)
    await pyautogui.click(gold)
    await pyautogui.click(gold)
    await asyncio.sleep(1)
    await pyautogui.locateCenterOnScreen("buy1.png") #clicks the buy button
    await asyncio.sleep(0.2)
    for i in range(6): #repeat 6 times to buy 7 packs
        await asyncio.sleep(0.2)
        await pyautogui.locateCenterOnScreen("up.png") #clicks the up arrow
    await pyautogui.locateCenterOnScreen("buy2.png") #clicks the buy button
    for i in range(10): #repeat 10 times cuz it was not working with 7
        await asyncio.sleep(1)
        await pyautogui.locateCenterOnScreen("continue.png") #clicks the continue button
    await asyncio.sleep(1)
    await pyautogui.locateCenterOnScreen("close.png") #clicks the close crown shop button
    await asyncio.sleep(0.5)
    await click_window_from_path(client.mouse_handler, client.root_window, crownsInvoiceClose) #closes invoice
    await client.send_key(Keycode.ENTER) #closes popup
    await feedPetCrumbs(client)

async def setup(): #activates all hooks that it can for a client
    handler = ClientHandler()
    print(f"Activating Special Lxghtend Hooks :O")
    async with ClientHandler() as handler:
        client = handler.get_new_clients()[0]
        await client.activate_hooks()
        await client.mouse_handler.activate_mouseless()
        await buyPetCrumbs(client)


async def main():
    print('Auto Pet Crumb Bot by Lxghtend')
    print('''Credits: notfaj - helped me with functions for reading text windows.
         starrfox - helped me out with everything.''')
    input('Press Enter when the pet you want to train is equipped and the Pet Bread Crumb Pack is the ONLY thing on your wishlist.')
    await setup()

    # Error Handling
async def run():
        try:
            await main()
        except:
         import traceback
         traceback.print_exc()
         print('Send this error to Lxghtend')

if __name__ == "__main__":
        asyncio.run(run())
