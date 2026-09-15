<?php
/**
 * Зависимости редактора блока.
 *
 * Без этого файла editor.js регистрируется без зависимостей и выполняется раньше
 * wp.blocks: блок молча не попадает в реестр редактора (проба этапа 12, D63).
 *
 * @package designstack-core
 */

return array(
	'dependencies' => array(
		'wp-blocks',
		'wp-element',
		'wp-block-editor',
		'wp-server-side-render',
	),
	'version'      => '1.0.0',
);
