import csv
import time
import urllib3
import re
import urllib.parse as urlparse
from io import StringIO
from bs4 import BeautifulSoup

def writeSpellRow(spellName, spellSchool, spellDescriptor, spellLevel, castTime, spellComp, spellRange, spellArea, spellEffect, spellTarget, spellDuration, savingThrow, spellRes, spellDesc, descFormatted, mystic, technomancer, spellLink):
	spellwriter.writerow({
		'name': spellName
		, 'school': spellSchool
		, 'subschool': ""
		, 'descriptor': spellDescriptor
		, 'spell_level': spellLevel
		, 'casting_time': castTime
		, 'resolve_points': resolvePoints
		, 'costly_components': spellComp
		, 'range': spellRange
		, 'area': spellArea
		, 'effect': spellEffect
		, 'targets': spellTarget
		, 'duration': spellDuration
		, 'dismissable': ""
		, 'shapeable': ""
		, 'saving_throws': savingThrow
		, 'spell_resistance': spellRes
		, 'description': spellDesc
		, 'description_formated': descFormatted
		, 'mystic': mystic
		, 'technomancer': technomancer
		, 'link': spellLink
		})
	return

def basicSpellInfo(readSpell):
	spellEffect, spellArea, spellTarget = None, None, None
	for spellInfo in readSpell:
		if "School" in spellInfo.get_text():
			schoolSplit = re.findall("School .+", spellInfo.text)[0].replace("School", "")
			if "(" in schoolSplit:
				spellSchool = schoolSplit.split("(", 1)[0]
				spellDescriptor = schoolSplit.split("(", 1)[1].strip("()")
			else:
				spellSchool = schoolSplit
				spellDescriptor = None
		castTime = re.findall("Casting Time .+", spellInfo.text)[0].replace("Casting Time", "") if "Casting Time" in spellInfo.text else None
		spellRange = re.findall("Range .+", spellInfo.text)[0].replace("Range", "") if "Range" in spellInfo.text else None
		if "Effect" in spellInfo.text: 
			if len(re.findall("Effect .+", spellInfo.text)) > 0:
				spellEffect = re.findall("Effect .+", spellInfo.text)[0].replace("Effect", "")
			else: 
				spellEffect = "see text"
		if "Area" in spellInfo.text: 
			if len(re.findall("Area .+", spellInfo.text)) > 0:
				spellArea = re.findall("Area .+", spellInfo.text)[0].replace("Area", "") 
			else: 
				spellArea = "see text"
		if "Targets" in spellInfo.text: 
			if len(re.findall("Targets .+", spellInfo.text)) > 0:
				spellTarget = re.findall("Targets .+", spellInfo.text)[0].replace("Targets", "") 
			else:
				spellTarget = "see text"
		spellDuration = re.findall("Duration .+", spellInfo.text)[0].replace("Duration", "") if "Duration" in spellInfo.text else None
		savingThrow = re.findall("Saving Throw .+", spellInfo.text)[0].replace("Saving Throw", "").rstrip("; ") if "Saving Throw" in spellInfo.text else None
		spellRes = re.findall("Spell Resistance .+", spellInfo.text)[0].replace("Spell Resistance", "") if "Spell Resistance" in spellInfo.text else None
		resolveRegex = re.compile(r"\d Resolve Point")
		resolvePoints = re.findall("\d", re.findall("\d Resolve Point", spellInfo.text)[0])[0] if resolveRegex.search(spellInfo.text) else None
	return spellSchool, spellDescriptor, castTime, spellRange, spellEffect, spellArea, spellTarget, spellDuration, savingThrow, spellRes, resolvePoints
			

url = 'http://www.starfindersrd.com/magic-and-spells/spells/'
regexUrl = re.compile(r"http://www.starfindersrd.com/magic-and-spells/spells/./.+")

pageOpen = urllib3.PoolManager()

spellsPage = pageOpen.request('GET', url).data

parsify = BeautifulSoup(spellsPage, "html.parser")

parsify.prettify()

with open('spells.csv', 'w') as csvfile:
	fields = ['name', 'school', 'subschool', 'descriptor', 'spell_level', 'casting_time', 'resolve_points', 'costly_components', 'range', 'area', 'effect', 'targets', 'duration', 'dismissable', 'shapeable', 'saving_throws', 'spell_resistance', 'description', 'description_formated', 'mystic', 'technomancer', 'link']
	spellwriter = csv.DictWriter(csvfile, fieldnames=fields, dialect='excel')
	spellwriter.writeheader()
	for anchor in parsify.findAll('a', href=True):
		if regexUrl.search(anchor['href']):
			spellSchool, castTime, spellSchoolDesc, spellDescriptor, spellComp, spellRange, spellEffect, spellArea, spellTarget, spellDuration, savingThrow, spellRes, spellListUrl = None, None, None, None, None, None, None, None, None, None, None, None, None
			mystic, technomancer, spellDesc, descFormatted, resolvePoints = "NULL", "NULL", "None", "None", 0
			readPage = pageOpen.request('GET', anchor['href'])
			readSpell = BeautifulSoup(readPage.data, "html.parser")
			spellTitle = readSpell.find('h1').text
			spellName = re.compile(r"[MT]\d|[MT]\s—|[MT]\d—\d|[MT]\d–\d").split(spellTitle, 1)[0].rstrip()
			print(spellName)
			spellLevel = re.compile(spellName).split(spellTitle, 1)[1].rstrip()
			if 'M' in spellLevel:
				spellListUrl = pageOpen.request('GET', "http://www.starfindersrd.com/magic-and-spells/mystic-spell-list/").data
				mysticRegex = (r"^[M]\d+$")
				if "—" in spellLevel and r"\d" not in spellLevel:
					mystic = "9"
				else:
					mystic = re.findall(r"\d", spellLevel[:spellLevel.find(mysticRegex) + len(mysticRegex)])[0]
				if "-" in spellLevel or "–" in spellLevel:
					spellLoop = re.findall(r"\d", spellLevel[:spellLevel.find(r"M\d-\d|M\d–\d") + len(mysticRegex)])
				else: 
					spellLoop = [mystic, mystic]
			if 'T' in spellLevel:
				spellListUrl = pageOpen.request('GET', "http://www.starfindersrd.com/magic-and-spells/technomancer-spell-list/").data
				techRegex = (r"^[T]\d$")
				if "—" in spellLevel and r"\d" not in spellLevel:
					technomancer = "9"
				else:
					technomancer = re.findall(r"\d", spellLevel[:spellLevel.find(techRegex) + len(techRegex)])[0]
				if '-' in spellLevel or "–" in spellLevel:
					spellLoop = re.findall(r"\d", spellLevel[:spellLevel.find(r"T\d-\d|T\d–\d") + len(techRegex)])
				else: 
					spellLoop = [technomancer, technomancer]
			loopTimes = int(spellLoop[1]) - int(spellLoop[0]) + 1
			i = 0
			spellDescArray = []
			for i in range(loopTimes):
				if (mystic != "NULL" and technomancer == "NULL"):
					spellLevel = "mystic " + str(mystic)
				if (mystic == "NULL" and technomancer != "NULL"):
					spellLevel = "technomancer " + str(technomancer)
				if technomancer == mystic:
					spellLevel = "mystic/technomancer " + str(mystic)
				spellList = BeautifulSoup(spellListUrl, "html.parser")
				spellList.prettify()
				for spellLevelHeader in spellList.find_all('h4'):
					if re.findall(r"\d", spellLevel)[0] in spellLevelHeader.get_text(): 
						for spellsInList in spellList.find_all('td'):
							if spellName in spellsInList.get_text(): 
								if spellsInList.nextSibling.nextSibling is None:
									if "Teleport" in spellName: spellDesc = "Instantly teleport as far as 2,000 miles."
									elif "Clairaudience/clairvoyance" in spellName: spellDesc = "Hear or see at a distance for 1 minute per level."
									elif "Summon Creature" in spellName: spellDesc = "Summons an extraplanar creature."
									elif "Miracle" in spellName: spellDesc == "Duplicate any mystic spell of 6th level or lower, or any other spell of 5th level or lower."
									elif "Wish" in spellName: spellDesc = "Duplicate any technomancer spell of 6th level or lower, or any other spell of 5th level or lower."
								else:
									spellDescArray.append(spellsInList.nextSibling.nextSibling.get_text())
									print(spellDescArray)
									spellDesc = spellDescArray[i]
									print(spellDesc)
								descFormatted = '<p>' + spellDesc + '</p>'
				for spellInfo in readSpell.find_all('p'):
					if "School" in spellInfo.get_text():
						schoolSplit = re.findall("School .+", spellInfo.text)[0].replace("School", "")
						if "(" in schoolSplit:
							spellSchool = schoolSplit.split("(", 1)[0]
							spellDescriptor = schoolSplit.split("(", 1)[1].strip("()")
						else:
							spellSchool = schoolSplit
					if "Casting Time" in spellInfo.text: castTime = re.findall("Casting Time .+", spellInfo.text)[0].replace("Casting Time", "")
					if "Range" in spellInfo.text: spellRange = re.findall("Range .+", spellInfo.text)[0].replace("Range", "")
					if "Effect" in spellInfo.text: 
						if len(re.findall("Effect .+", spellInfo.text)) > 0:
							spellEffect = re.findall("Effect .+", spellInfo.text)[0].replace("Effect", "")
						else: 
							spellEffect = "see text"
					if "Area" in spellInfo.text: 
						if len(re.findall("Area .+", spellInfo.text)) > 0:
							spellArea = re.findall("Area .+", spellInfo.text)[0].replace("Area", "") 
						else: 
							spellArea = "see text"
					if "Targets" in spellInfo.text: 
						if len(re.findall("Targets .+", spellInfo.text)) > 0:
							spellTarget = re.findall("Targets .+", spellInfo.text)[0].replace("Targets", "") 
						else:
							spellTarget = "see text"
					if "Duration" in spellInfo.text: spellDuration = re.findall("Duration .+", spellInfo.text)[0].replace("Duration", "")
					if "Saving Throw" in spellInfo.text: savingThrow = re.findall("Saving Throw .+", spellInfo.text)[0].replace("Saving Throw", "").rstrip("; ")
					if "Spell Resistance" in spellInfo.text: spellRes = re.findall("Spell Resistance .+", spellInfo.text)[0].replace("Spell Resistance", "")
					resolveRegex = re.compile(r"\d Resolve Point")
					if resolveRegex.search(spellInfo.text): 
						resolvePoints = re.findall("\d", re.findall("\d Resolve Point", spellInfo.text)[0])[0]
				writeSpellRow(spellName, spellSchool, spellDescriptor, spellLevel, castTime, spellComp, spellRange, spellArea, spellEffect, spellTarget, spellDuration, savingThrow, spellRes, spellDesc, descFormatted, mystic, technomancer, anchor['href'])
				if "mystic" in spellLevel: 
					mystic = int(mystic) + 1
				else:
					technomancer = int(technomancer) + 1
				i += 1
				time.sleep(3)