/**
 * Редактор блока «Все уроки».
 *
 * Настроек нет: данные приходят из уроков, в редакторе показывается сам блок.
 */
( function ( blocks, element, blockEditor, ServerSideRender ) {
	'use strict';

	var el = element.createElement;

	blocks.registerBlockType( 'designstack/lessons-index', {
		edit: function ( props ) {
			return el(
				'div',
				blockEditor.useBlockProps(),
				el( ServerSideRender, {
					block: 'designstack/lessons-index',
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
