// Copyright (c) 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/**
 * Get the current URL.
 *
 * @param {function(string)} callback - called when the URL of the current tab
 *   is found.
 */
function getCurrentTabUrl(callback) {
  // Query filter to be passed to chrome.tabs.query - see
  // https://developer.chrome.com/extensions/tabs#method-query
  var queryInfo = {
    active: true,
    currentWindow: true
  };

  chrome.tabs.query(queryInfo, function(tabs) {
    // chrome.tabs.query invokes the callback with a list of tabs that match the
    // query. When the popup is opened, there is certainly a window and at least
    // one tab, so we can safely assume that |tabs| is a non-empty array.
    // A window can only have one active tab at a time, so the array consists of
    // exactly one tab.
    var tab = tabs[0];

    // A tab is a plain object that provides information about the tab.
    // See https://developer.chrome.com/extensions/tabs#type-Tab
    var url = tab.url;

    // tab.url is only available if the "activeTab" permission is declared.
    // If you want to see the URL of other tabs (e.g. after removing active:true
    // from |queryInfo|), then the "tabs" permission is required to see their
    // "url" properties.
    console.assert(typeof url == 'string', 'tab.url should be a string');

    callback(url);
  });

  // Most methods of the Chrome extension APIs are asynchronous. This means that
  // you CANNOT do something like this:
  //
  // var url;
  // chrome.tabs.query(queryInfo, function(tabs) {
  //   url = tabs[0].url;
  // });
  // alert(url); // Shows "undefined", because chrome.tabs.query is async.
}

/**
 * @param {string} searchTerm - Search term for Google Image search.
 * @param {function(string,number,number)} callback - Called when an image has
 *   been found. The callback gets the URL, width and height of the image.
 * @param {function(string)} errorCallback - Called when the image is not found.
 *   The callback gets a string that describes the failure reason.
 */
function getProductDetails(searchTerm, callback, errorCallback) {
  // Google image search - 100 searches per day.
  // https://developers.google.com/image-search/
  var parser = document.createElement('a');
  parser.href = searchTerm;
  var pat = /\/(B[A-Z0-9]{8,9})$/
  var pid = 'BOGUS'
  if (pat.test(parser.pathname)){
    pid = pat.exec(parser.pathname)[1];
  }
  else {
    pat = /\/(B[A-Z0-9]{8,9})[\/\?]/
    pid = pat.exec(parser.pathname) || 'BOGUS'
  }
  var searchUrl = 'http://localhost:5000/' + parser.hostname + '/' + pat.exec(parser.pathname)[1]
  console.log(searchUrl)
  var x = new XMLHttpRequest();
  x.open('GET', searchUrl);
  // The Google image search API responds with JSON, so let Chrome parse it.
  x.responseType = 'json';
  x.onload = function() {
    // Parse and process the response from Google Image Search.
    var response = x.response;
    console.log(response)
    if (!response) {
      errorCallback('Product not in DataBase?');
      return;
    }
    callback(response.result,response.status);
  };
  x.onerror = function() {
    errorCallback('Network error.');
  };
  setTimeout(function(){if (document.getElementById('status').textContent!=''){renderStatus('Product is new for us, processing..');document.getElementById('prog').style.display=''};}, 6000)
  x.send();
}

function renderStatus(statusText) {
  document.getElementById('status').textContent = statusText;
}

document.addEventListener('DOMContentLoaded', function() {

  getCurrentTabUrl(function(url) {
    // Put the image URL in Google search.
    renderStatus('Fetching the Reviews For the Product...');
    getProductDetails(url, function(result,status) {
      document.getElementById('prog').style.display='none'
      if (status==200){
        renderStatus('');
        var table = document.getElementById('rev-table');
        table.tHead.style.display =''
        var i = 1
        for (var key in result) {
        	if (result.hasOwnProperty(key) && key!='_id' && key!='domain') {
        		var row = table.insertRow(i);
        		var cell0 = row.insertCell(0);
        		var cell1 = row.insertCell(1);
        		var cell2 = row.insertCell(2);
        		cell0.innerHTML = key;
        		cell1.innerHTML = result[key];
        		cell2.innerHTML = 'Lorem ipsum. Lets win this thing.'
        		var i = i + 1;
        	}
        }
      }
      else {
        renderStatus('Something Went Wrong...')
      }
      // Explicitly set the width/height to minimize the number of reflows. For
      // a single image, this does not matter, but if you're going to embed
      // multiple external images in your page, then the absence of width/height
      // attributes causes the popup to resize multiple times.

    }, function(errorMessage) {
      renderStatus('Cannot display ratings. ' + errorMessage);
    });
  });
});


