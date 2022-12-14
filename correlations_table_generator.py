import math
import sqlite3
from decimal import *
from PREFS import dbPath

#SQLITE CONNECTION
conn = sqlite3.connect(dbPath)
c = conn.cursor()

#SET ITEMS LIST
themes = [2833226,5871901,253220,2703099,1264247,168737,2826493,2189918,2819356,2708562,4363266,4287447,4519990,5556590,5484319,3810895,6221179,5177775,4106987,5489609,6434280,7758048,7315054,9512331,9323981,4021469,6776630,8819050,11776839,13373220,9228123,9545812,6339019,13304399,9602611,11118909,10695119,10648488,11099136,9553045,13080328,10439297,7824993]

#IF WE NEED FULL LIST OF ITEMS FOR EACH ITEM (WITHOUT MERGING DATA FROM TWO COLUMNS)
crossDuplication = True

#CUTOFF SHARE (WE IGNORE ITEMS SETS WITH RATIO LESS THAN ignoreRatio)
ignoreRatio = 100

#HERE WE LOG INTO OUTSIDE FILE
with open('file.txt', 'w+n') as file:
	
	themes_titles = []

	for id in range(0, len(themes)):

			#print c.execute("SELECT `Item_title` FROM `__themes_list` WHERE `Item_id`='" + str(themes[id]) + "'").fetchone()

			for title in c.execute("SELECT `Item_title` FROM `__themes_list` WHERE `Item_id`='" + str(themes[id]) + "'"):
					themes_titles.append(title[0])
					

	#SET SALES ARRAY
	sales = []

	#SET TIME RANGE
	rangeFrom = '2017-01-22'
	rangeTo = '2017-06-11'

	#CORRELATIONS MATH FUNCTION
	#ignoreRatio is available share of representative data
	def corr(array1, array2, ignoreRatio):
		
		Ex = 0
		Ey = 0
		Exy = 0
		Ex2 = 0
		Ey2 = 0
		arraysLength = len(array1)
		#print "arraysLength",arraysLength
		
		#GET LIST WITH MOST NULL VALUES (weakest link)
		nullsShare = max(array1.count('null'), array2.count('null'))
		
		#print nullsShare
		file.write("nullsShare: "+str(nullsShare)+ " \n")
		
		#MATH SHARE PERCENT
		listFullness = 100 - (float(Decimal(100) / Decimal(arraysLength)) * nullsShare)
			
		#print 'listFullness:',listFullness,'arraysLength',arraysLength,'nullsShare',nullsShare
		file.write('listFullness: '+str(listFullness)+' arraysLength: '+str(arraysLength)+' nullsShare: '+str(nullsShare)+ " \n")
		
		if listFullness >= ignoreRatio:
		
			#!if length of arrays is equal!
			for value in range(0, len(array1)):

				x = array1[value]
				y = array2[value]

				if(x != 'null' and y != 'null'):
					
					Ex += x
					Ey += y
					Exy += x*y
					Ex2 += x*x
					Ey2 += y*y

				else:

					arraysLength = arraysLength - 1

			#print 'Ex',Ex,'Ey',Ey,'Exy',Exy,'Ex2',Ex2,'Ey2',Ey2
			
			if Ex != 0 or Ey !=0:
				
				_e = (arraysLength * Exy - Ex * Ey)
				_e1 = math.sqrt((arraysLength * Ex2 - Ex*Ex) * (arraysLength * Ey2 - Ey*Ey))
				
				if _e !=0 or _e1 !=0:
					
					r = _e / _e1
				
				else:
			
					#r = 'DivErr'
					#r = 'Divide by Zero Error'
					r = -2
				
			else:
				
				#r = 'DivErr'
				#r = 'Divide by Zero Error'
				r = -2
		else:
			
			r = 'Data is not complete/representative'
			
		return r



	for theme in range(0, len(themes)):

		tempArr = []
		
		for sale in c.execute("SELECT `Sales` FROM '" + str(themes[theme]) + "' WHERE `Sales_period`>='" + rangeFrom + "' AND `Sales_period`<='" + rangeTo + "'"):
		
			if sale[0] != 'null':
				tempArr.append(int(sale[0]))
			else:
				tempArr.append('null')
			
		#print tempArr
		sales.append(tempArr)
		
		

	arrLen = len(themes)

	invertConcatList = []

	#REPLACE TABLE
	c.execute("DROP TABLE IF EXISTS `correlations_2015plus`")
	c.execute("CREATE TABLE `correlations_2015plus` (`id1` int, `item1` char, `id2` int, `item2` char, `item1_array_density` int, `item2_array_density` int, `minimal_arrays_density` int, `correlation` float)")

	for item in range(0,arrLen):

		for sec_item in range(0,arrLen):

			invConc = str(themes[sec_item]) + "," + str(themes[item])
			normConc = str(themes[item]) + "," + str(themes[sec_item])
			
			##print 'invConc:',invConc,'normConc:',normConc

			if themes[item] != themes[sec_item]:

				if crossDuplication != True  and normConc in invertConcatList :
				
					1+1

				else:

					invertConcatList.append(invConc)
					
					item1 = themes_titles[item].encode('utf-8', 'ignore')
					item2 = themes_titles[sec_item].encode('utf-8', 'ignore')

					correl = str(corr(sales[item],sales[sec_item], ignoreRatio))

					listFullness_item1 = 100 - (float(Decimal(100) / Decimal(len(sales[item]))) * sales[item].count('null'))
					listFullness_item2 = 100 - (float(Decimal(100) / Decimal(len(sales[sec_item]))) * sales[sec_item].count('null'))
					minItemsFullness = str(  min(listFullness_item1, listFullness_item2)  )
					
					if correl != 'Data is not complete/representative':
						#print 'execute:', 'correl returns', correl, '[item1:','"'+item1+'"', 'item2:','"'+item2+'"]'
						c.execute("insert into `correlations_2015plus` values ('"
							+ str(themes[item]) +"', '"
							+ item1 +"', '"
							+ str(themes[sec_item]) +"', '"
							+ item2 +"', '"
							+ str(  listFullness_item1  ) +"', '"
							+ str(  listFullness_item2  ) +"',  '"
							+ minItemsFullness +"', '"
							+ correl +"')")
						
						file.write('execute: correl returns: ' + correl + ' [item1: "' + item1 + '"item2: "' + item2 + '"]' + '\n')
					
					else:

						#print correl
						1+1
					
			else:
				1+1
				#print 'keys duplicates'

	#CREATE TABLE `correlations_2015plus` (`item1` INT NULL,`item2` INT NULL)

	conn.commit()

	# We can also close the cursor if we are done with it
	c.close()
