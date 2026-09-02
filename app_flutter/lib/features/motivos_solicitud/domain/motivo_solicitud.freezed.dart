// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'motivo_solicitud.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MotivoSolicitud {

 int get id; int get laboratorioId; String get nombre; String get codigo; String get estado; String get createdAt; String get updatedAt; int? get createdBy; int? get updatedBy;
/// Create a copy of MotivoSolicitud
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MotivoSolicitudCopyWith<MotivoSolicitud> get copyWith => _$MotivoSolicitudCopyWithImpl<MotivoSolicitud>(this as MotivoSolicitud, _$identity);

  /// Serializes this MotivoSolicitud to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MotivoSolicitud&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.codigo, codigo) || other.codigo == codigo)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,codigo,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'MotivoSolicitud(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, codigo: $codigo, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class $MotivoSolicitudCopyWith<$Res>  {
  factory $MotivoSolicitudCopyWith(MotivoSolicitud value, $Res Function(MotivoSolicitud) _then) = _$MotivoSolicitudCopyWithImpl;
@useResult
$Res call({
 int id, int laboratorioId, String nombre, String codigo, String estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy
});




}
/// @nodoc
class _$MotivoSolicitudCopyWithImpl<$Res>
    implements $MotivoSolicitudCopyWith<$Res> {
  _$MotivoSolicitudCopyWithImpl(this._self, this._then);

  final MotivoSolicitud _self;
  final $Res Function(MotivoSolicitud) _then;

/// Create a copy of MotivoSolicitud
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? codigo = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,}) {
  return _then(MotivoSolicitud(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,codigo: null == codigo ? _self.codigo : codigo // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [MotivoSolicitud].
extension MotivoSolicitudPatterns on MotivoSolicitud {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MotivoSolicitud value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MotivoSolicitud() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MotivoSolicitud value)  $default,){
final _that = this;
switch (_that) {
case _MotivoSolicitud():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MotivoSolicitud value)?  $default,){
final _that = this;
switch (_that) {
case _MotivoSolicitud() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String codigo,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MotivoSolicitud() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.codigo,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String codigo,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)  $default,) {final _that = this;
switch (_that) {
case _MotivoSolicitud():
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.codigo,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int laboratorioId,  String nombre,  String codigo,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)?  $default,) {final _that = this;
switch (_that) {
case _MotivoSolicitud() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.codigo,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MotivoSolicitud implements MotivoSolicitud {
  const _MotivoSolicitud({required this.id, required this.laboratorioId, required this.nombre, required this.codigo, required this.estado, required this.createdAt, required this.updatedAt, this.createdBy, this.updatedBy});
  factory _MotivoSolicitud.fromJson(Map<String, dynamic> json) => _$MotivoSolicitudFromJson(json);

@override final  int id;
@override final  int laboratorioId;
@override final  String nombre;
@override final  String codigo;
@override final  String estado;
@override final  String createdAt;
@override final  String updatedAt;
@override final  int? createdBy;
@override final  int? updatedBy;

/// Create a copy of MotivoSolicitud
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MotivoSolicitudCopyWith<_MotivoSolicitud> get copyWith => __$MotivoSolicitudCopyWithImpl<_MotivoSolicitud>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MotivoSolicitudToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MotivoSolicitud&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.codigo, codigo) || other.codigo == codigo)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,codigo,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'MotivoSolicitud(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, codigo: $codigo, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class _$MotivoSolicitudCopyWith<$Res> implements $MotivoSolicitudCopyWith<$Res> {
  factory _$MotivoSolicitudCopyWith(_MotivoSolicitud value, $Res Function(_MotivoSolicitud) _then) = __$MotivoSolicitudCopyWithImpl;
@override @useResult
$Res call({
 int id, int laboratorioId, String nombre, String codigo, String estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy
});




}
/// @nodoc
class __$MotivoSolicitudCopyWithImpl<$Res>
    implements _$MotivoSolicitudCopyWith<$Res> {
  __$MotivoSolicitudCopyWithImpl(this._self, this._then);

  final _MotivoSolicitud _self;
  final $Res Function(_MotivoSolicitud) _then;

/// Create a copy of MotivoSolicitud
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? codigo = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,}) {
  return _then(_MotivoSolicitud(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,codigo: null == codigo ? _self.codigo : codigo // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
