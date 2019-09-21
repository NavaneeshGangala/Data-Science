Following 14 currency codes are considered for the analysis
	AED
	AUD
	CAD
	CZK
	EUR
	GBP
	HKD
	JPY
	MXN
	NOK
	NZD
	SGD
	THB
	USD


Data File Contents :
1. 3yrFxHistoryDataFor14Currency.zip :
	It has Forex 3 year history data for INR to 14 different currencies

	File Format:
		Timestamp: Timestamp of the Forex rate record in the format "2019-09-02T23:59:00Z",
		Rate: the exchange rate (double/decimal value),
		From: From Currency (Foreign Currency code)
		To : To currency (INR)
		Source: Source from where this data has been taken,

	sample record:
		2019-09-02T23:59:00Z,87.25125093464992,GBP,INR,dbsfxtrade.com

2. StreamingForexGenerator.zip: 
	Python based on Forex Generator tool for streaming the realtime rates through socket. ForexGeneratorReadme.md has been provided for more details about the program.
	
3. Preconfigured notifications for random 5000 users for Forex.
	File Format:
		UserAccountId: ACccount Number of the user.
		UserName : Name of the User who needs to be notified
		RequiredCurrency : Currency which is required in exchange with INR
		ForexRate : Forex rate desired by the customer for notification(1 Foreign Currency to INR rate)
		TransferAmount : Desired Amount to Transfer.
		


		
		