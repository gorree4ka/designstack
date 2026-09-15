/**
 * Редактор блока «Проверка грейда».
 *
 * Настроек нет: вопросы собираются из карты компетенций, в редакторе показывается сам блок.
 */
( function ( blocks, element, blockEditor, ServerSideRender ) {
	'use strict';

	var el = element.createElement;

	blocks.registerBlockType( 'designstack/grade-check', {
		edit: function ( props ) {
			return el(
				'div',
				blockEditor.useBlockProps(),
				el( ServerSideRender, {
					block: 'designstack/grade-check',
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
