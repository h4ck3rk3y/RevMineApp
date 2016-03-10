// Called when the url of a tab changes.
function checkForValidUrl(tabId, changeInfo, tab) {
// If the tabs url starts with "http://specificsite.com"...
  var pat = /\/B[A-Z0-9]{8,9}/
  var isbn_pat = /\/[0-9]{10}/
  var snap_pat = /\/[0-9]{12}/
  var flip_pat = /itm[a-z0-9]{13}/i
  if (  (pat.test(tab.url) || isbn_pat.test(tab.url) || snap_pat.test(tab.url) || flip_pat.test(tab.url)) == true && (tab.url.indexOf('www.amazon.in') !=-1 || tab.url.indexOf('www.snapdeal.com') !=-1 || tab.url.indexOf('www.flipkart.com') !=-1) ){
    chrome.pageAction.show(tabId);
  }
};

chrome.tabs.onUpdated.addListener(checkForValidUrl);
