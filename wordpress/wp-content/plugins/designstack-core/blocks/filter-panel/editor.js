/**
 * Редактор блока «Панель фильтров».
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;

	blocks.registerBlockType( 'designstack/filter-panel', {
		edit: function ( props ) {
			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el(
						components.PanelBody,
						{ title: __( 'Вид', 'designstack-core' ) },
						el( components.SelectControl, {
							label: __( 'Вариант', 'designstack-core' ),
							value: props.attributes.variant,
							options: [{"label": "Колонка слева", "value": "sidebar"}, {"label": "Панель снизу", "value": "sheet"}],
							onChange: function ( value ) {
								props.setAttributes( { variant: value } );
							}
						} )
					)
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/filter-panel',
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
