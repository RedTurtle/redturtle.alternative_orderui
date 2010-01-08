/**
 * Javascript code for the reordering support
 */

registerPloneFunction(function () {
	var js_baseurl = jq("#js_baseurl").text();
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
				event.preventDefault();
				var choosen = prompt("Inserisci la nuova posizione per l'elemento alla posizione "+i);
				if (choosen != null) {
					var v = parseInt(choosen)-1;
					var upOrDown = (v<i?'up':'down');
					var delta = (v<i?-(v-i):(v-i));
					document.location.href = js_baseurl + "/folder_position?position="+upOrDown+"&amp;id="+el.attr("id").replace("cnt_","")+"&delta="+delta;
				}
			});
		});
});
