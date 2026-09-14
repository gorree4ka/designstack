/**
 * Редактор блока «Факты о ресурсе».
 *
 * Блок берёт запись из контекста, поэтому вне страницы ресурса превью пустое.
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;

	blocks.registerBlockType( 'designstack/resource-meta', {
		edit: function ( props ) {
			var attributes = props.attributes;

			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el(
						components.PanelBody,
						{ title: __( 'Что показываем', 'designstack-core' ) },
						el( components.TextControl, {
							label: __( 'Только эти поля, через запятую', 'designstack-core' ),
							help: __( 'Пусто — показываем все заполненные поля ресурса.', 'designstack-core' ),
							value: ( attributes.fields || [] ).join( ', ' ),
							onChange: function ( value ) {
								var fields = value
									.split( ',' )
									.map( function ( item ) {
										return item.trim();
									} )
									.filter( Boolean );

								props.setAttributes( { fields: fields } );
							}
						} ),
						el( components.ToggleControl, {
							label: __( 'Показывать темы', 'designstack-core' ),
							checked: !! attributes.showTopics,
							onChange: function ( value ) {
								props.setAttributes( { showTopics: value } );
							}
						} )
					)
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/resource-meta',
						attributes: attributes,
						urlQueryArgs: { post_id: props.context && props.context.postId }
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
