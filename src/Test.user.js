// ==UserScript==
// @name         Send trusted input example
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  try to take over the world!
// @author       You
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @match      *://*/*
// @grant unsafeWindow
// @grant window.close
// @grant window.focus
// @grant window.onurlchange
// @grant GM_openInTab
// @grant GM_registerMenuCommand
// @run-at  context-menu
// ==/UserScript==

// require http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js
// require https://gist.github.com/raw/2625891/waitForKeyElements.js

const URL = 'https://www.google.com/'
const CSS_SEL_GOOGLE_SEARCH = "div.RNNXgb"
const CSS_SEL_GOOGLE_SEARCH_BTN = ".FPdoLc"

const REQ_CLICK = 'REQ CLICK ${X} ${Y}'
const REQ_KEYS = 'REQ KEYS ${K}'
const DONE = 'DONE'
const NEW_WINDOW_TITLE = 'RUN'


function log_ex(message, loc) {
	const sourceUrl = `${loc.origin}${loc.pathname}`;
    const log_exMessage = `%c${message} %c@${sourceUrl}`;
    console.log(log_exMessage, 'color: blue;', 'color: green;');
}


function getClientPosPx(elem, posAtMiddle){
	// Returns approximate position in pixels (px) relative to window corner

	let rect = elem.getBoundingClientRect();
	let screen_scale = window.devicePixelRatio;

	// relative to page corner
	// (not from window corner, skips window menu area)
	let elem_x_px = (posAtMiddle? (rect.left + rect.right) / 2 : rect.x) * screen_scale;
	let elem_y_px = (posAtMiddle? (rect.bottom + rect.top) / 2 : rect.y) * screen_scale;

	// page corner relative to window corner
	let page_x_px = (window.outerWidth - window.innerWidth)/2 * screen_scale;
	let page_y_px = (window.outerHeight - window.innerHeight) * screen_scale;

	let x = Math.round(page_x_px + elem_x_px);
	let y = Math.round(page_y_px + elem_y_px);
	return {x:x, y:y}
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function waitUntilDone() {
	let delay = 200
	for (let i = 0; i < 5000; i++)
		{
		await sleep(200)
        if (document.title == DONE)
            return;
		if (i % 50 == 0)
			log_ex(`Waiting for trusted command ${i * delay}ms`, location);
		}
}


async function trustedClick(elem)
	{
	let xy = getClientPosPx(elem, true)
	document.title = REQ_CLICK.replace('${X}', xy.x).replace('${Y}', xy.y);
    await waitUntilDone();
	}


async function trustedKeys(elem, keys)
	{
	elem.focus()
	document.title = REQ_KEYS.replace('${K}', keys);
    await waitUntilDone();
	}


async function main()
	{
	if (document.location.href != URL) {
		log_ex('Correct URL not detected, skipping main', location)
		return;
	}
	// await sleep(400)
	// if (document.title != NEW_WINDOW_TITLE) {
	//	log_ex('Title not changed, try run script via context menu', location)
	//	return;
	//} else {
	//	log_ex('run_loop', location)
	//}

    let search = document.querySelector(CSS_SEL_GOOGLE_SEARCH)
	await trustedClick(search)
    await trustedKeys(search, 'H e l l o W o r l d')
    let btn = document.querySelector(CSS_SEL_GOOGLE_SEARCH_BTN)
    await trustedClick(btn)
	}


async function open_new_tab_workaround(){
	if (document.location.href == URL)
		return;

	log_ex('New tab is yet desired because WinApi fails to set window caption to DONE on usual tab,\n' +
		   'but it works on tab opened with UserScript.\n' +
	       'Skipping DONE and relying on passive checks is an option without new window.\n' +
	       'Switching to network comm instead of caption is also a suggestion', location)

	log_ex('open_new_tab', location)
	let w = window.outerWidth;
	let h = window.outerWidth;
	let windowFeatures = `width=${w},height=${h},left=0,top=0`

	// currentURL = window.location.href
	let wnd = window.open(URL, "_blank", windowFeatures);
	if (!wnd) {
		log_ex('Cannot reference a new window, possibly popup was blocked.', location)
		return;
	}
}


open_new_tab_workaround()
main()
