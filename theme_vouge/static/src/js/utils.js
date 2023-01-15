/** @odoo-module **/

export function isImg(node) {
    return (node && (node.nodeName === "IMG" || (node.className && node.className.match(/(^|\s)(media_iframe_video|o_image|fa|lnr|icon|icofont|lni|ri|ti)(\s|$)/i))));
}
