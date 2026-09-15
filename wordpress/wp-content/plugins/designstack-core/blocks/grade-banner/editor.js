/**
 * Редактор блока «Баннер проверки грейда».
 *
 * Настроек нет: текст и фото приходят из настроек сайта, в редакторе показывается сам блок.
 */
( function ( blocks, element, blockEditor, ServerSideRender ) {
	'use strict';

	var el = element.createElement;

	blocks.registerBlockType( 'designstack/grade-banner', {
		edit: function ( props ) {
			return el(
				'div',
				blockEditor.useBlockProps(),
				el( ServerSideRender, {
					block: 'designstack/grade-banner',
					attributes: props.attributes
				} )
			);
		},
		save: function () {
			return null;
		}
	} );
} )(
	window.wp.blocks,
	window.wp.element,
	window.wp.blockEditor,
	window.wp.serverSideRender
);
