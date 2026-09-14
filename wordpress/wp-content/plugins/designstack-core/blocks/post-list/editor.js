/**
 * Редактор блока «Карточки записей».
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;
	var controls = [{"key": "category", "label": "Раздел", "options": [{"label": "Подборки", "value": "collections"}, {"label": "Дайджест", "value": "digest"}, {"label": "Обзоры", "value": "reviews"}]}, {"key": "variant", "label": "Заголовок", "options": [{"label": "Свежие", "value": "fresh"}, {"label": "Другие", "value": "other"}]}];

	blocks.registerBlockType( 'designstack/post-list', {
		edit: function ( props ) {
			var fields = controls.map( function ( control ) {
				return el( components.SelectControl, {
					key: control.key,
					label: control.label,
					value: props.attributes[ control.key ],
					options: control.options,
					onChange: function ( value ) {
						var patch = {};
						patch[ control.key ] = value;
						props.setAttributes( patch );
					}
				} );
			} );

			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el( components.PanelBody, { title: __( 'Что показываем', 'designstack-core' ) }, fields )
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/post-list',
						attributes: props.attributes
					} )
				)
			);
		},
		save: function () {
			return null;
		}
	} );
} )(
	window.wp.blocks,
	window.wp.element,
	window.wp.components,
	window.wp.blockEditor,
	window.wp.serverSideRender,
	window.wp.i18n
);
