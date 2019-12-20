# REST client for the UW Notification Web Service                                    
                                                                                
[![Build Status](https://api.travis-ci.com/uw-it-aca/uw-restclients-nws.svg?branch=master)](https://travis-ci.com/uw-it-aca/uw-restclients-nws)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-restclients-nws/badge.svg?branch=master)](https://coveralls.io/github/uw-it-aca/uw-restclients-nws?branch=master)
[![PyPi Version](https://img.shields.io/pypi/v/uw-restclients-nws.svg)](https://pypi.python.org/pypi/uw-restclients-nws)
![Python versions](https://img.shields.io/pypi/pyversions/uw-restclients-nws.svg)

Installation:                                                                   
                                                                                
    pip install UW-RestClients-NWS                                              
                                                                                
To use this client, you'll need these settings in your application or script:   
                                                                                
    # Specifies whether requests should use live or mocked resources,           
    # acceptable values are 'Live' or 'Mock' (default)                          
    RESTCLIENTS_NWS_DAO_CLASS='Live'                                            
                                                                                
    # Paths to UWCA cert and key files                                          
    RESTCLIENTS_NWS_CERT_FILE='/path/to/cert'                                   
    RESTCLIENTS_NWS_KEY_FILE='/path/to/key'                                     
                                                                                
    # Notification Web Service hostname (eval or production)                         
    RESTCLIENTS_NWS_HOST='...'                      
                                                                                
Optional settings:                                                              
                                                                                
    # Customizable parameters for urllib3                                       
    RESTCLIENTS_NWS_TIMEOUT=5                                                   
    RESTCLIENTS_NWS_POOL_SIZE=10                                                
                                                                                
See examples for usage.  Pull requests welcome.
