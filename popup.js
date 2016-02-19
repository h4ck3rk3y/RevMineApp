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
  var isbn_pat = /\/([0-9]{10})/
  var snap_pat = /\/([0-9]{12})/
  var flip_pat = /(itm[a-z0-9]{13})/i
  var flip_pat_name = /\/([a-zA-Z\-0-9]+)\/p/
  var snap_pat_name = /product\/([a-zA-Z\-0-9]+)/

  var pid = 'BOGUS'
  var prod_name = 'NAME'

  if (pat.test(parser.pathname)){
    pid = pat.exec(parser.pathname)[1];
  }
  else if(snap_pat.test(parser.pathname)){
  	pid = snap_pat.exec(parser.pathname)[1].toString();
  	prod_name = snap_pat_name.exec(parser.pathname)[1].toString();
  }
  else if(flip_pat.test(parser.pathname)){
  	pid = flip_pat.exec(parser.pathname)[1].toString();
  	prod_name = flip_pat_name.exec(parser.pathname)[1].toString();
  }
  else if(isbn_pat.test(parser.pathname)){
    pid = isbn_pat.exec(parser.pathname)[1].toString();
  }
  else {
    pat = /\/(B[A-Z0-9]{8,9})[\/\?]/
    pid = pat.exec(parser.pathname)[1] || 'BOGUS'
  }

  var searchUrl = 'http://localhost:5000/' + parser.hostname + '/' + pid + '/' + prod_name
  console.log(searchUrl)
  var x = new XMLHttpRequest();
  x.timeout = 400000;
  x.open('GET', searchUrl);
  // The Google image search API responds with JSON, so let Chrome parse it.
  x.responseType = 'json';
  x.onload = function() {
    // Parse and process the response from Google Image Search.
    var response = x.response;
    if (!response) {
      errorCallback('Something went wrong. Contact @h4ck3rk3y?');
      return;
    }
    callback(response.result,response.status,response.reviews);
  };
  x.onerror = function() {
    errorCallback('Network error.');
  };
  setTimeout(function(){if (document.getElementById('status').textContent=='Fetching insights for the product...'){renderStatus('Product is new for us, processing..');document.getElementById('prog').style.display=''};}, 6000)
  x.send();
}

function renderStatus(statusText) {
  document.getElementById('status').textContent = statusText;
}

document.addEventListener('DOMContentLoaded', function() {

  getCurrentTabUrl(function(url) {
    // Put the image URL in Google search.
    renderStatus('Fetching insights for the product...');
    getProductDetails(url, function(result,status, reviews) {
      document.getElementById('prog').style.display='none'
      if (status==200){
        renderStatus('');
        var table = document.getElementById('canvas');
        canvas.style.display='';
        var ctx = document.getElementById("canvas").getContext("2d");
        var barChartData ={}
        barChartData.labels = []
        barChartData.datasets= []
        barChartData.datasets.push({fillColor : "rgba(51,178,63,0.5)",strokeColor : "rgba(51,178,63,0.8)",highlightFill: "rgba(51,178,63,0.75)"
      ,highlightStroke: "rgba(51,178,63,1)"});
        barChartData.datasets[0].data = []
        var i = 1;
        for (var key in result) {
        	if (result.hasOwnProperty(key) && key!='_id' && key!='domain') {
        	 barChartData.labels.push(key);
           barChartData.datasets[0].data.push(result[key])
          }
        }

        window.myBar = new Chart(ctx).Bar(barChartData, {
          responsive : true
        });

		$("#canvas").click(
		    function(evt){
		        var activePoints = myBar.getBarsAtEvent(evt);
		        console.log(activePoints[0]);
		        /* do something */
		    }
		);

        console.log(reviews);
        var $mq = $('#anim');

        function showRandomMarquee() {
          var rannum = Math.floor(Math.random()*reviews.length);
          $mq
            .marquee('destroy')
            .bind('finished', function(){document.getElementById('anim').innerHTML = reviews[rannum];
          setTimeout(function(){showRandomMarquee()},4000);})
            .html(reviews[rannum])
            .marquee({duration: 250, direction:'down'});
        }


        showRandomMarquee();
      }
      else if(status==100) {
        renderStatus('Not enough reviews on the product...One day though?')
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

$(document).ready(function() {
    //set initial state.
    $('#light_mode').change(function() {
        if($(this).is(":checked")) {
            $("body").css("background",'rgba(0, 0, 0, 0) none repeat scroll 0% 0% / auto padding-box border-box');
            $("body").css("color","rgba(0, 0, 0, 0.870588)");
            document.getElementById('symbol').innerHTML = '&#9789;'
        }
        else{
            $("body").css("background","#1a1a1a")
            $("body").css("color","#eaeaea")
            document.getElementById('symbol').innerHTML = '&#9728;'
        }
    });
});