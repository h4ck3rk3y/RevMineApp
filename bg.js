// Called when the url of a tab changes.
function checkForValidUrl(tabId, changeInfo, tab) {
// If the tabs url starts with "http://specificsite.com"...
  var pat = /\/B[A-Z0-9]{8,9}/
  var isbn_pat = /\/[0-9]{9}/
  if (((pat.test(tab.url) || isbn_pat.test(tab.url)) == true && tab.url.indexOf('www.amazon.in'))){
    chrome.pageAction.show(tabId);
  }
};

chrome.tabs.onUpdated.addListener(checkForValidUrl);
