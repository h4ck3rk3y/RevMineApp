// Called when the url of a tab changes.
function checkForValidUrl(tabId, changeInfo, tab) {
// If the tabs url starts with "http://specificsite.com"...
  var pat = /\/B[A-Z0-9]{8,9}/
  if ((pat.test(tab.url) == true && tab.url.indexOf('www.amazon.in')) || tab.url.indexOf('flipkart.com')> 0 || tab.url.indexOf('snapdeal.com')> 0){
    chrome.pageAction.show(tabId);
  }
};

chrome.tabs.onUpdated.addListener(checkForValidUrl);
