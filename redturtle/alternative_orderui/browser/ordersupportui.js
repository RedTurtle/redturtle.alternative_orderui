/**
 * Javascript code for the reordering support
 */

registerPloneFunction(function () {
	var js_baseurl = jq("#js_baseurl").text();
	var querystring = window.location.search;
	var qspos = querystring.indexOf("pagenumber");
	var qsn = '';
	if (qspos>-1) {
		// read the pagenumber argument
		 qsn = "&pagenumber="+querystring.substr(qspos+11, qspos+12);
	}
	jq("#listing-table tr").find("td:first").each(function (i) {
		jq(this).find("input:first").after('&nbsp;<span class="discreet order-index">'+(i+1)+'</span>');			
	});
	
	jq("#listing-table tr").find("td:last")
	    .each(function (i) {
			var el = jq(this);
			el.empty()
				.append('&nbsp;<a href="javascript:;" class="reorder-cmd">'
			          +'<img alt="" src="++resource++move_16x16.gif" />'
					  +'</a>');
			jq(".reorder-cmd", el).click(function(event) {
				// event.preventDefault();
				var choosen = prompt("Inserisci la nuova posizione per l'elemento alla posizione "+(i+1));
				if (choosen != null) {
					var v = parseInt(choosen)-1;
					var upOrDown = (v<i?'up':'down');
					var delta = (v<i?-(v-i):(v-i));
					var show_all = "";
					if (querystring.indexOf("show_all=true")>-1) {
						show_all= "&show_all=true";
					}
					window.location.href = js_baseurl + "/folder_position?position="+upOrDown+"&amp;id="+el.attr("id").replace("cnt_","")+"&delta="+delta+show_all+qsn;
				}
			});
		});
});
