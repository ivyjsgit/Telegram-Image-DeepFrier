import cv2
import numpy as np
import sys
import urllib
import telegram
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from urllib.request import urlopen
from os import path, listdir
import os
import getpass


def argInstructions():
    """ Shows what the script uses, what args it uses and what it does. """
    """ Only put images in the input folder, everything in the input folder will tried to be converted in images on the output folder.  """
    print ("Needs: Python 3, numpy and OpenCV")
    print ("Usage: <inputFolder> <outputFolder='output/'>")
    print ("Does: Deep Fries the images in a folder and output them at the output folder")


def printFolders(inputFolder, outputFolder):
    """
    Shows the input folder and the output folder
    :param inputFolder: string | inputFolder | Input folder path
    :param outputFolder: string | outputFolder | Output folder path
    """
    print ("Showing the input and output folders: ")
    print ("Input folder:\t" + inputFolder)
    print ("Output folder:\t" + outputFolder)


def processArgs():
    """
    Process the args for use in the script
    """

    inputFolder = sys.argv[1]
    outputFolder = sys.argv[2]
    if len(sys.argv) >= 3:
        pass
    else:
        'Output'
    return inputFolder, outputFolder


def fryImage(imagePath):
    """
    Passes the image path, opens it with OpenCV and returns the image with drastic posterization
    :param imagePath: string | imagePath | Full image path
    """
    imageStart = cv2.imread(imagePath)
    return badPosterize(imageStart)

def fryURL(url):
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	return badPosterize(image)

def badPosterize(imageNormal):
    """
    Posterize the image through a color list, diving it and making a pallete.
    Finally, applying to the image and returning the image with a the new pallete
    :param imageNormal: CV opened image | imageNormal | The normal image opened with OpenCV
    """
    colorList = np.arange(0, 256)
    colorDivider = np.linspace(0, 155,3)[1]
    colorQuantization = np.int0(np.linspace(0, 150, 2))
    colorLevels = np.clip(np.int0(colorList/colorDivider), 0, 1)
    colorPalette = colorQuantization[colorLevels]
    return colorPalette[imageNormal]


def folderCheck(inputFolder, outputFolder):
    """
    It receives the folder, get all files and make a pair for each open file
    After that, each pair is posterized and is saved at lower quality.
    With the image being fryed and being saved at the output folder plus a "-fry" for the fried one.
    :param inputFolder: string | inputFolder | Input folder path
    :param outputFolder: string | outputFolder | Output folder path
    """
    namePairs = [path.splitext(nameWithFormat) for nameWithFormat in listdir(inputFolder)]

    for (fileName, formatName) in namePairs:
        imageOpen = cv2.imread(path.join(inputFolder, fileName + formatName))
        imageFry = badPosterize(imageOpen)
        cv2.imwrite(path.join(outputFolder, fileName + '-fry.jpg'), imageFry, [int(cv2.IMWRITE_JPEG_QUALITY), 0])

    return len(namePairs)


def imageresponder(bot, update):
	print("Attempting to download image")
	photo = update.message.photo[1]
	print(photo.file_id)
	imageURL = photo.get_file().file_path
	print(imageURL)
	deepfriedImage = (fryURL(imageURL))
	print("Deep fried image!")
	print("Send image")
	# cv2.imshow("asdf",deepfriedImage)
	fileName = photo.file_id+".jpg"
	cv2.imwrite(fileName, deepfriedImage, [int(cv2.IMWRITE_JPEG_QUALITY), 0])
	openedFile = open(fileName, 'rb')
	bot.sendPhoto(update.message.chat_id, openedFile)
	print("Preparing to delete " + fileName)
	os.remove(fileName)
	print("Got image!")


APIKey = getpass.getpass("API Key:")
bot = telegram.Bot(token = APIKey)
updater = Updater(APIKey)
dispatcher = updater.dispatcher
message_handler = MessageHandler(Filters.photo, imageresponder)
dispatcher.add_handler(message_handler)
updater.start_polling()
